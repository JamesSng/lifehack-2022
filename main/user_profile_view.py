from flask import render_template, redirect, request, flash
import awstools

def user_profile(user):
    userinfo = awstools.getCurrentUserInfo()
    profileinfo = awstools.getVolunteerInfo(user)
    tags = awstools.getEventTypes()
    data = awstools.getVolunteeringInterests(user)
    awstools.getVolunteeringHours(user)
    eventlist = awstools.getEventsFromVolunteer(user)
    friends = awstools.getFriendsFromVolunteer(user)
    for i in eventlist:
        i['organiserid'] = i['organiser']
        i['organiser'] = awstools.getOrganiserInfo(i['organiserid'])['name']
    if request.method == 'POST':
        if profileinfo['username'] not in userinfo['friends']:
            awstools.addFriend(userinfo['username'], profileinfo['username'])
            flash('Friend added!', 'success')
            return redirect(f'/profile/{user}')
        else:
            awstools.removeFriend(userinfo['username'], profileinfo['username'])
            flash('Friend removed!', 'success')
            return redirect(f'/profile/{user}')
    return render_template('user_profile.html', userinfo=userinfo, profileinfo=profileinfo, tags=tags, data=data, eventlist=eventlist, friends=friends)

