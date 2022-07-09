from flask import render_template, redirect, request, flash
import awstools

def organiser_event(event):
    userinfo = awstools.getCurrentUserInfo()
    eventinfo = awstools.getEventInfo(event)
    if userinfo == None or userinfo['usertype'] != 1 or userinfo['organiserid'] != eventinfo['organiser']:
        flash('You cannot edit this event', 'danger')
        return redirect(f'/event/{event}')

    organiserinfo = awstools.getOrganiserInfo(eventinfo['organiser'])
    participants = awstools.getVolunteersFromEvent(event)

    if request.method == 'POST':
        result = request.form
        
        title = result['title']
        description = result['description']
        date = result['date']
        hours = result['hours']
        num_occurrences = result['num_occurrences']
        etype = result['etype']
        location = result['location']
        url = result['url']

        info = {}
        info['eventid'] = event
        info['title'] = title
        info['description'] = description
        info['date'] = date
        try:
            info['hours'] = float(hours)
        except:
            info['hours'] = eventinfo['hours']
            flash('Invalid duration format')
        info['num_occurrences'] = num_occurrences
        info['type'] = etype
        info['location'] = location
        info['url'] = url
        info['organiser'] = userinfo['organiserid']
        info['participants'] = eventinfo['participants']
        awstools.updateEventInfo(event, info)
        return redirect(f'/edit_event/{event}')

    return render_template('organiser_event.html', userinfo=userinfo, eventinfo=eventinfo, participants=participants)



