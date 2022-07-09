from flask import render_template, redirect, request, flash
import awstools

def organiser_profile(user):
    userinfo = awstools.getCurrentUserInfo()
    profileinfo = awstools.getOrganiserInfo(user)
    eventlist = awstools.getEventsFromOrganiser(user)
    profileinfo['bio'] = profileinfo['bio'].replace('\n', '<br>')
    ages, locations = awstools.getOrganiserAnalytics(user)

    if request.method == 'POST':
        result = request.form

        eventid = result['eventid']
        if not eventid:
            flash('Please enter a event ID!', 'warning')
        elif type(awstools.getEventInfo(eventid)) != str:
            flash('Event ID is taken!', 'warning')
        else:
            awstools.createEventFromId(eventid, profileinfo['organiserid'])
            return redirect(f'/edit_event/{eventid}')
    return render_template('organiser_profile.html', userinfo=userinfo, profileinfo=profileinfo, eventlist=eventlist, ages=ages, locations=locations)


