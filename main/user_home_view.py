from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def user_home():
    eventlist = awstools.getAllEvents()
    for event in eventlist:
        info = awstools.getOrganiserInfo(event['organiser'])
        event['organiser'] = info['name']
    return render_template('user_home.html', userinfo=awstools.getCurrentUserInfo(), eventlist=eventlist)

