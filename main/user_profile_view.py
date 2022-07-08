from flask import render_template, redirect, request
import awstools

def user_profile(user):
    userinfo = awstools.getCurrentUserInfo()
    profileinfo = awstools.getVolunteerInfo(user)
    tags = awstools.getEventTypes()
    data = awstools.getVolunteeringInterests(user)
    awstools.getVolunteeringHours(user)
    eventlist = awstools.getEventsFromVolunteer(user)
    friends = awstools.getFriendsFromVolunteer(user)
    return render_template('user_profile.html', userinfo=userinfo, profileinfo=profileinfo, tags=tags, data=data, eventlist=eventlist, friends=friends)

