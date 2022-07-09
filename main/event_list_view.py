from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def event_list():
    userinfo = awstools.getCurrentUserInfo()
    eventlist = awstools.getAllEventsFriends()
    for event in eventlist:
        info = awstools.getOrganiserInfo(event['organiser'])
        event['organiser'] = info['name']
    tags = awstools.getEventTypes()
    if userinfo != None and userinfo['usertype'] == 0:
        data = awstools.getVolunteeringInterests(userinfo['username'])
    else:
        data = []

    if request.method == 'POST':
        result = request.form

        lowDate = result['lowDate']
        highDate = result['highDate']
        etype = result['etype']
        if etype == 'All':
            etype = None
        friends = 'friends' in result
        eventlist = awstools.getFilteredEvents(lowDate=lowDate, highDate=highDate, etype=etype, friends=friends)
    return render_template('event_list.html', userinfo=userinfo, eventlist=eventlist, tags=tags, data=data)

