import boto3
from boto3.dynamodb.conditions import Key
from flask import session
import os
from hashlib import sha256
from datetime import datetime, timedelta
import csv
import json

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

dynamodb = boto3.resource('dynamodb')
volunteers_table = dynamodb.Table('volunteers')
organisers_table = dynamodb.Table('organisers')
events_table = dynamodb.Table('events')
blog_table = dynamodb.Table('blog')
misc_table = dynamodb.Table('misc')

s3 = boto3.client('s3', 'us-west-2')
s3_resources = boto3.resource('s3')
MATERIALS_BUCKET_NAME = 'lifehack-materials'

lambda_client = boto3.client('lambda')

def parseDate(dateString):
    return datetime.strptime(dateString, '%d/%m/%Y')

# Scanning dynamoDB
def scan(table, ProjectionExpression = None, ExpressionAttributeNames = None, ExpressionAttributeValues = None):
    results = []
    if ProjectionExpression == None:
       # No Expression Attribute Names
        resp = table.scan()
        results = results + resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ExclusiveStartKey = resp['LastEvaluatedKey']
            )
            results = results + resp['Items']
    elif ExpressionAttributeNames != None and ExpressionAttributeValues != None:
        resp = table.scan(
            ProjectionExpression=ProjectionExpression,
            ExpressionAttributeNames = ExpressionAttributeNames,
            ExpressionAttributeValues = ExpressionAttributeValues
        )
        results = results + resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ProjectionExpression=ProjectionExpression,
                ExpressionAttributeNames = ExpressionAttributeNames,
                ExpressionAttributeValues = ExpressionAttributeValues,
                ExclusiveStartKey = resp['LastEvaluatedKey']
            )
            results = results + resp['Items']

    elif ExpressionAttributeNames != None:
        resp = table.scan(
            ProjectionExpression=ProjectionExpression,
            ExpressionAttributeNames = ExpressionAttributeNames,
        )
        results = results + resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ProjectionExpression=ProjectionExpression,
                ExpressionAttributeNames = ExpressionAttributeNames,
                ExclusiveStartKey = resp['LastEvaluatedKey']
            )
            results = results + resp['Items']
    elif ExpressionAttributeValues != None:
        resp = table.scan(
            ProjectionExpression=ProjectionExpression,
            ExpressionAttributeValues = ExpressionAttributeValues
        )
        results = results + resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ProjectionExpression=ProjectionExpression,
                ExpressionAttributeValues = ExpressionAttributeValues,
                ExclusiveStartKey = resp['LastEvaluatedKey']
            )
            results = results + resp['Items']
    else:
        resp = table.scan(
            ProjectionExpression=ProjectionExpression,
        )
        results = results + resp['Items']
        while 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ProjectionExpression=ProjectionExpression,
                ExclusiveStartKey = resp['LastEvaluatedKey']
            )
            results = results + resp['Items']
    return results

def getAllVolunteers():
	value = scan(volunteers_table)
	return value

def getAllOrganisers():
	value = scan(organisers_table)
	return value

def getAllEvents():
    value = scan(events_table)
    return value

def getAllBlogPosts():
    value = scan(blog_table)
    return value

def getAllEventsFriends():
    value = scan(events_table)
    userinfo = getCurrentUserInfo()
    if userinfo == None or userinfo['usertype'] == 1: #organiser
        for event in value:
            event['numfriends'] = 0
    else:
        for event in value:
            event['numfriends'] = 0
            for friend in userinfo['friends']:
                if friend in event['participants']:
                    event['numfriends'] += 1
    return value

def getFilteredEvents(lowDate=None, highDate=None, etype=None, friends=False, text=None):
    events = getAllEventsFriends()
    if lowDate:
        low = parseDate(lowDate) 
        events = [i for i in events if low <= parseDate(i['date'])]
    if highDate:
        high = parseDate(highDate)
        events = [i for i in events if parseDate(i['date']) <= high]
    if etype:
        events = [i for i in events if i['type'] == etype]
    if text:
        events = [i for i in events if (text in i['title'] or text in i['description'])]
    if friends:
        events.sort(reverse=True, key=lambda i: i['numfriends'])
    return events

def getVolunteerInfo(username):
	response = volunteers_table.query(
		KeyConditionExpression = Key('username').eq(username)
	)
	info = response['Items']
	if len(info) != 1:
		return "This volunteer doesn't exist"
	return info[0]

def getOrganiserInfo(organiserid):
	response = organisers_table.query(
		KeyConditionExpression = Key('organiserid').eq(organiserid)
	)
	info = response['Items']
	if len(info) != 1:
		return "This organiser doesn't exist"
	return info[0]

def getEventInfo(eventid):
	response = events_table.query(
		KeyConditionExpression = Key('eventid').eq(eventid)
	)
	info = response['Items']
	if len(info) != 1:
		return "This event doesn't exist"
	return info[0]

def getBlogInfo(blogid):
	response = blog_table.query(
		KeyConditionExpression = Key('blogid').eq(int(blogid))
	)
	info = response['Items']
	if len(info) != 1:
		return "This blog doesn't exist"
	return info[0]

def updateVolunteerInfo(username, info):
    volunteers_table.update_item(
        Key = {'username': username},
        UpdateExpression = f'set birthdate=:b, events=:d, friends=:e, #g=:g, #h=:h, phone=:i, password=:j',
        ExpressionAttributeValues = {':b':info['birthdate'], ':d':info['events'], ':e':info['friends'], ':g':info['location'], ':h':info['name'], ':i':info['phone'], ':j':info['password']},
        ExpressionAttributeNames = {'#g':'location', '#h':'name'}
    )

def createVolunteer(name, username, phone, birthdate, location, password):
    info = {}
    info['name'] = name
    info['username'] = username
    info['phone'] = phone
    info['birthdate'] = birthdate
    info['location'] = location
    info['password'] = hashPassword(password)
    info['friends'] = []
    info['events'] = []
    updateVolunteerInfo(username, info)

def updateOrganiserInfo(organiserid, info):
	organisers_table.update_item(
        Key = {'organiserid': organiserid},
        UpdateExpression = f'set #a=:a, bio=:b, events=:c, password=:d',
        ExpressionAttributeValues = {':a':info['name'], ':b':info['bio'], ':c':info['events'], ':d':info['password']},
        ExpressionAttributeNames = {'#a':'name'}
    )

def createOrganiser(name, username, bio, password):
    info = {}
    info['name'] = name
    info['organiserid'] = username
    info['bio'] = bio
    info['password'] = hashPassword(password)
    info['events'] = []
    updateOrganiserInfo(username, info)

def updateEventInfo(eventid, info):
	events_table.update_item(
        Key = {'eventid': eventid},
        UpdateExpression = f'set #b=:b, num_occurrences=:c, organiser=:d, participants=:e, hours=:f, #g=:g, description=:h, title=:i, #j=:j, #k=:k',
        ExpressionAttributeValues = {':b':info['date'], ':c':info['num_occurrences'], ':d':info['organiser'], ':e':info['participants'], ':f':info['hours'], ':g':info['location'], ':h':info['description'], ':i':info['title'], ':j':info['type'], ':k':info['url']},
        ExpressionAttributeNames = {'#b':'date', '#g':'location', '#j':'type', '#k':'url'}
    )

def updateBlogInfo(blogid, info):
    blog_table.update_item(
        Key = {'blogid': int(blogid)},
        UpdateExpression = f'set authorid=:a, authorname=:b, authortype=:c, content=:d, #e=:e, published=:f, tags=:g, title=:h, #i=:i',
        ExpressionAttributeValues = {':a':info['authorid'], ':b':info['authorname'], ':c':info['authortype'], ':d':info['content'], ':e':info['date'], ':f':info['published'], ':g':info['tags'], ':h':info['title'], ':i':info['url']},
        ExpressionAttributeNames = {'#e':'date', '#i':'url'}
    )

def hashPassword(password):
    hh = sha256()
    hh.update(password.encode('utf-8'))
    return hh.hexdigest()

def checkVolunteerPassword(username, password):
    info = getVolunteerInfo(username)
    if type(info) == str:
        return False
    return info['password'] == hashPassword(password)

def checkOrganiserPassword(username, password):
    info = getOrganiserInfo(username)
    if type(info) == str:
        return False
    return info['password'] == hashPassword(password)

def login(usertype, userid):
    for key in list(session.keys()):
        session.pop(key)
    session['usertype'] = usertype
    session['userid'] = userid
    session.permanent = True

def logout():
    for key in list(session.keys()):
        session.pop(key)

def getCurrentUserInfo():
    try:
        usertype = dict(session)['usertype']
        userid = dict(session)['userid']
        if usertype == 0:
            info = getVolunteerInfo(userid)
        else:
            info = getOrganiserInfo(userid)
        info['usertype'] = usertype
        return info
    except KeyError as e:
        return None
    return None

def addEventToVolunteer(username, eventid):
    userinfo = getVolunteerInfo(username)
    if eventid not in userinfo['events']:
        userinfo['events'].append(eventid)
    updateVolunteerInfo(username, userinfo)
    eventinfo = getEventInfo(eventid)
    if username not in eventinfo['participants']:
        eventinfo['participants'].append(username)
    updateEventInfo(eventid, eventinfo)

def removeEventFromVolunteer(username, eventid):
    userinfo = getVolunteerInfo(username)
    if eventid in userinfo['events']:
        userinfo['events'].remove(eventid)
    updateVolunteerInfo(username, userinfo)
    eventinfo = getEventInfo(eventid)
    if username in eventinfo['participants']:
        eventinfo['participants'].remove(username)
    updateEventInfo(eventid, eventinfo)

def addEventToOrganiser(organiserid, eventid):
    userinfo = getOrganiserInfo(organiserid)
    if eventid not in userinfo['events']:
        userinfo['events'].append(eventid)
    updateOrganiserInfo(organiserid, userinfo)

def removeEventFromOrganiser(organiserid, eventid):
    userinfo = getOrganiserInfo(organiserid)
    if eventid in userinfo['events']:
        userinfo['events'].remove(eventid)
    updateOrganiserInfo(organiserid, userinfo)

def addFriend(username, friend):
    userinfo = getVolunteerInfo(username)
    if friend not in userinfo['friends']:
        userinfo['friends'].append(friend)
    updateVolunteerInfo(username, userinfo)

def removeFriend(username, friend):
    userinfo = getVolunteerInfo(username)
    if friend in userinfo['friends']:
        userinfo['friends'].remove(friend)
    updateVolunteerInfo(username, userinfo)

def getEventsFromVolunteer(username):
    userinfo = getVolunteerInfo(username)
    eventids = userinfo['events']
    events = []
    for event in eventids:
        events.append(getEventInfo(event))
    return events

def getEventsFromOrganiser(username):
    userinfo = getOrganiserInfo(username)
    eventids = userinfo['events']
    events = []
    for event in eventids:
        events.append(getEventInfo(event))
    return events

def getVolunteersFromEvent(eventid):
    eventinfo = getEventInfo(eventid)
    users = []
    for user in eventinfo['participants']:
        users.append(getVolunteerInfo(user))
    return users

def getFriendsFromVolunteer(username):
    userinfo = getVolunteerInfo(username)
    friendids = userinfo['friends']
    friends = []
    for friend in friendids:
        friends.append(getVolunteerInfo(friend))
    return friends

def getEventTypes():
    return ['Children and Youth', 'Seniors', 'Environment', 'Underprivileged People', 'Arts and Heritage']

def getVolunteeringInterests(username):
    events = getEventsFromVolunteer(username)
    types = {}
    for i in getEventTypes():
        types[i] = 0
    total = 0
    for eventinfo in events:
        print(eventinfo['eventid'])
        types[eventinfo['type']] += 1
        total += 1
    res = []
    for key, value in types.items():
        if total != 0:
            res.append(int(value / total * 100))
        else:
            res.append(0)
    return res

def getVolunteeringHours(username):
    events = getEventsFromVolunteer(username)
    dates = {}
    now = datetime.now()
    for eventinfo in events:
        date = parseDate(eventinfo['date'])
        for i in range(int(eventinfo['num_occurrences'])):
            datestr = date.strftime('%Y-%m-%d')
            if datestr not in dates:
                dates[datestr] = 0
            dates[datestr] += eventinfo['hours']
            date += timedelta(days = 7)
            if date > now:
                break

    file = open(f'resources/{username}.csv', 'w')
    writer = csv.writer(file)
    for key, value in dates.items():
        writer.writerow([key, value])
    file.close()

def processAnalytics(eventids):
    userids = []
    for event in eventids:
        eventinfo = getEventInfo(event)
        for participant in eventinfo['participants']:
            if participant not in userids:
                userids.append(participant)

    ages = {}
    locations = {}
    year = datetime.now().year
    for user in userids:
        userinfo = getVolunteerInfo(user)
        age = year - parseDate(userinfo['birthdate']).year
        if age not in ages:
            ages[age] = 0
        ages[age] += 1
        location = userinfo['location']
        if location not in locations:
            locations[location] = 0
        locations[location] += 1
    
    return ages, locations

def getOrganiserAnalytics(organiserid):
    organiserinfo = getOrganiserInfo(organiserid)
    eventids = organiserinfo['events']
    return processAnalytics(eventids)

def getEventAnalytics(eventid):
    return processAnalytics([eventid])

def uploadEventResource(files, eventid):
    s3.upload_fileobj(files, MATERIALS_BUCKET_NAME, f'{eventid}.zip', ExtraArgs={"ACL": 'public-read', "ContentType":files.content_type})

def getPublishedBlogs():
	response = misc_table.query(
		KeyConditionExpression = Key('item').eq('publishedblogs')
	)
	info = response['Items']
	if len(info) != 1:
		return []
	return info[0]['blogs']

def updatePublishedBlogs(blogs):
    misc_table.update_item(
        Key = {'item': 'publishedblogs'},
        UpdateExpression = f'set blogs=:a',
        ExpressionAttributeValues = {':a':blogs}
    )

def publishBlog(blogid):
    info = getBlogInfo(blogid)
    info['published'] = True
    updateBlogInfo(blogid, info)

    blogs = getPublishedBlogs()
    if blogid not in blogs:
        blogs.append(blogid)
    updatePublishedBlogs(blogs)

def unpublishBlog(blogid):
    info = getBlogInfo(blogid)
    info['published'] = False
    updateBlogInfo(blogid, info)

    blogs = getPublishedBlogs()
    if blogid in blogs:
        blogs.remove(blogid)
    updatePublishedBlogs(blogs)

def getNextBlogId():
    res = lambda_client.invoke(
        FunctionName = 'arn:aws:lambda:us-west-2:669016928924:function:next-blog-id',
        InvocationType = 'RequestResponse'
    )
    blog_index = json.load(res["Payload"])
    return blog_index['blogId']

if __name__ == '__main__':
    print(getNextBlogId())
    print(getNextBlogId())
    print(getNextBlogId())
