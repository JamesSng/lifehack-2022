from flask import render_template, redirect, request, flash
from decimal import *
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
        files = request.files
        
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
            info['hours'] = Decimal(hours)
        except:
            info['hours'] = Decimal(eventinfo['hours'])
            flash('Invalid duration format', 'warning')
        try:
            if int(num_occurrences) < 1:
                info['num_occurrences'] = int(eventinfo['num_occurrences'])
                flash('Invalid value of number of occurrences', 'warning')
            else:
                info['num_occurrences'] = int(num_occurrences)
        except:
            info['num_occurrences'] = int(eventinfo['num_occurrences'])
            flash('Invalid number of occurrences format', 'warning')
        info['type'] = etype
        info['location'] = location
        info['url'] = url
        info['organiser'] = userinfo['organiserid']
        info['participants'] = eventinfo['participants']
        info['resources'] = eventinfo['resources']
        awstools.updateEventInfo(event, info)

        if 'resources' in files and files['resources'].filename != '':
            if '.' not in files['resources'].filename or files['resources'].filename.rsplit('.', 1)[1].lower() != 'zip':
                flash('Invalid file format', 'warning')
            else:
                awstools.uploadEventResource(files['resources'], event)
                flash('Resources uploaded!', 'success')

        return redirect(f'/edit_event/{event}')

    return render_template('organiser_event.html', userinfo=userinfo, eventinfo=eventinfo, participants=participants)



