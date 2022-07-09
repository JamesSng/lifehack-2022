from flask import render_template, redirect, request, flash
import awstools

def user_event(event):
    userinfo = awstools.getCurrentUserInfo()
    eventinfo = awstools.getEventInfo(event)
    eventinfo['numfriends'] = 0
    organiserinfo = awstools.getOrganiserInfo(eventinfo['organiser'])
    participants = awstools.getVolunteersFromEvent(event)
    sort_participants = participants

    if userinfo != None and userinfo['usertype'] == 0:
        for friend in userinfo['friends']:
            if friend in eventinfo['participants']:
                eventinfo['numfriends'] += 1
        sort_participants = []
        for i in participants:
            if i['username'] == userinfo['username']:
                sort_participants.append(i)
        for i in participants:
            if i['username'] in userinfo['friends']:
                sort_participants.append(i)
        for i in participants:
            if i not in sort_participants:
                sort_participants.append(i)

    others = awstools.getEventsFromOrganiser(eventinfo['organiser'])
    others = [i for i in others if i != eventinfo]
    for event2 in others:
        info = awstools.getOrganiserInfo(event2['organiser'])
        event2['organiser'] = info['name']
    if request.method == 'POST':
        if userinfo['username'] not in eventinfo['participants']:
            awstools.addEventToVolunteer(userinfo['username'], eventinfo['eventid'])
            flash('Registration successful!', 'success')
            return redirect(f'/event/{event}')
        else:
            awstools.removeEventFromVolunteer(userinfo['username'], eventinfo['eventid'])
            flash('Registration removed', 'success')
            return redirect(f'/event/{event}')
    return render_template('user_event.html', userinfo=userinfo, eventinfo=eventinfo, organiserinfo=organiserinfo, participants=sort_participants, others=others)



