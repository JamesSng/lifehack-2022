from flask import render_template, redirect, request
import awstools

def organiser_profile(user):
    userinfo = awstools.getCurrentUserInfo()
    profileinfo = awstools.getOrganiserInfo(user)
    eventlist = awstools.getEventsFromOrganiser(user)
    profileinfo['bio'] = profileinfo['bio'].replace('\n', '<br>')
    ages, locations = awstools.getOrganiserAnalytics(user)
    print(ages)
    print(locations)
    return render_template('organiser_profile.html', userinfo=userinfo, profileinfo=profileinfo, eventlist=eventlist, ages=ages, locations=locations)


