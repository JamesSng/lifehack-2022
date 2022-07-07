import boto3
from boto3.dynamodb.conditions import Key
from flask import session
import os
from hashlib import sha256
from datetime import datetime, timedelta
import csv

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

dynamodb = boto3.resource('dynamodb')
volunteers_table = dynamodb.Table('volunteers')
organisers_table = dynamodb.Table('organisers')
events_table = dynamodb.Table('events')

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
    info['friends'] = {}
    info['events'] = {}
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
    info['events'] = {}
    updateOrganiserInfo(username, info)

def updateEventInfo(eventid, info):
	events_table.update_item(
        Key = {'eventid': eventid},
        UpdateExpression = f'set #b=:b, num_occurrences=:c, organiser=:d, participants=:e, hours=:f, #g=:g, description=:h, title=:i, type=:j, url=:k',
        ExpressionAttributeValues = {':b':info['date'], ':c':info['num_occurrences'], ':d':info['organiser'], ':e':info['participants'], ':f':info['hours'], ':g':info['location'], ':h':info['description'], ':i':info['title'], ':j':info['type'], ':k':info['url']},
        ExpressionAttributeNames = {'#b':'date', '#g':'location'}
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

def removeEventFromVolunteer(username, eventid):
    userinfo = getVolunteerInfo(username)
    if eventid in userinfo['events']:
        userinfo['events'].remove(eventid)
    updateVolunteerInfo(username, userinfo)

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

def getEventsFromVolunteer(username):
    userinfo = getVolunteerInfo(username)
    eventids = userinfo['events']
    events = []
    for event in eventids:
        events.append(getEventInfo(event))
    return events

def getEventTypes():
    return ['Children and Youth', 'Seniors', 'Environment', 'Underpriveleged People', 'Arts and Heritage']

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
        res.append(int(value / total * 100))
    return res

def getVolunteeringHours(username):
    events = getEventsFromVolunteer(username)
    dates = {}
    now = datetime.now()
    for eventinfo in events:
        date = datetime.strptime(eventinfo['date'], '%d/%m/%Y')
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

if __name__ == '__main__':
    getVolunteeringHours('alien')
