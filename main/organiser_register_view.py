from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def get_template():
    return render_template('organiser_register.html', userinfo=awstools.getCurrentUserInfo())

def organiser_register():
    if request.method == 'POST':
        result = request.form

        name = result['name']
        username = result['username']
        bio = result['bio']
        password = result['password']
        password2 = result['password2']

        if not (name and username and password and password2):
            flash('Please fill in all fields!', 'warning')
            return get_template()
        if type(awstools.getOrganiserInfo(username)) != str:
            flash('Sorry, username is taken', 'warning')
            return get_template()
        if password != password2:
            flash('Passwords do not match!', 'warning')
            return get_template()

        awstools.createOrganiser(name, username, bio, password)
        flash(f'Welcome {username}!', 'success')
        return redirect('/')
    return get_template()


