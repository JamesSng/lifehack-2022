from flask import render_template, redirect, request, flash
import awstools

def user_event(event):
    userinfo = awstools.getCurrentUserInfo()
    eventinfo = awstools.getEventInfo(event)
    organiserinfo = awstools.getOrganiserInfo(eventinfo['organiser'])
    participants = awstools.getVolunteersFromEvent(event)
    others = awstools.getEventsFromOrganiser(eventinfo['organiser'])
    for event in others:
        info = awstools.getOrganiserInfo(event['organiser'])
        event['organiser'] = info['name']
    if request.method == 'POST':
        if userinfo['username'] not in eventinfo['participants']:
            awstools.addEventToVolunteer(userinfo['username'], eventinfo['eventid'])
            flash('Registration successful!', 'success')
            return redirect(f'/event/{event.eventid}')
        else:
            awstools.removeEventFromVolunteer(userinfo['username'], eventinfo['eventid'])
            flash('Registration removed', 'success')
            return redirect(f'/event/{event.eventid}')
    return render_template('user_event.html', userinfo=userinfo, eventinfo=eventinfo, organiserinfo=organiserinfo, participants=participants, others=others)



