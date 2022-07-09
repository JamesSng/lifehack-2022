from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools
import ai

def user_home():
    userinfo = awstools.getCurrentUserInfo()
    eventlist = awstools.getAllEventsFriends()
    for event in eventlist:
        info = awstools.getOrganiserInfo(event['organiser'])
        event['organiser'] = info['name']
    tags = awstools.getEventTypes()
    if userinfo != None and userinfo['usertype'] == 0:
        data = awstools.getVolunteeringInterests(userinfo['username'])
        topfiveids = ai.suggest_user(userinfo['username'])[:5]
        topfive = []
        for eventid in topfiveids:
            topfive.append(awstools.getEventInfo(eventid))
    else:
        data = []
        topfive = []

    if request.method == 'POST':
        result = request.form

        lowDate = result['lowDate']
        highDate = result['highDate']
        etype = result['etype']
        if etype == 'All':
            etype = None
        friends = 'friends' in result
        print(lowDate)
        print(highDate)
        print(etype)
        print(friends)

        eventlist = awstools.getFilteredEvents(lowDate=lowDate, highDate=highDate, etype=etype, friends=friends)
        print('filtered')
    return render_template('user_home.html', userinfo=userinfo, eventlist=eventlist, tags=tags, data=data, topfive=topfive)

