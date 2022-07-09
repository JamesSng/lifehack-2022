from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools
import ai

def user_home():
    userinfo = awstools.getCurrentUserInfo()
    eventlist = awstools.getAllEventsFriends()
    friendsmap = dict()
    for event in eventlist:
        info = awstools.getOrganiserInfo(event['organiser'])
        event['organiser'] = info['name']
        event['organiserid'] = info['organiserid']
        friendsmap[event['eventid']] = event['numfriends']
    tags = awstools.getEventTypes()
    if userinfo != None and userinfo['usertype'] == 0:
        data = awstools.getVolunteeringInterests(userinfo['username'])
        topfiveids = ai.suggest_user(userinfo['username'])[:5]
        topfive = []
        for eventid in topfiveids:
            event = awstools.getEventInfo(eventid)
            event['numfriends'] = friendsmap[eventid]
            event['organiserid'] = event['organiser']
            event['organiser'] = awstools.getOrganiserInfo(event['organiserid'])['name']
            topfive.append(event)
    else:
        data = []
        topfive = []

    if request.method == 'POST':
        result = request.form

        lowDate = result['lowDate']
        highDate = result['highDate']
        if lowDate and not awstools.check_date(lowDate):
            lowDate = ''
            flash('Invalid lowDate format!', 'warning')
        if highDate and not awstools.check_date(highDate):
            highDate = ''
            flash('Invalid highDate format!', 'warning')
        
        etype = result['etype']
        if etype == 'All':
            etype = None
        friends = 'friends' in result

        eventlist = awstools.getFilteredEvents(lowDate=lowDate, highDate=highDate, etype=etype, friends=friends)
    return render_template('user_home.html', userinfo=userinfo, eventlist=eventlist, tags=tags, data=data, topfive=topfive)

