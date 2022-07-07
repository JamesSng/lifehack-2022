from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools
from datetime import datetime

def check_date(date):
    try:
        datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        return False
    return True

def get_template():
    return render_template('user_register.html', userinfo=awstools.getCurrentUserInfo())

def user_register():
    if request.method == 'POST':
        result = request.form

        name = result['name']
        username = result['username']
        phone = result['phone']
        birthdate = result['birthdate']
        location = result['location']
        password = result['password']
        password2 = result['password2']

        if not (name and username and phone and birthdate and location and password and password2):
            flash('Please fill in all fields!', 'warning')
            return get_template()
        if type(awstools.getVolunteerInfo(username)) != str:
            flash('Sorry, username is taken', 'warning')
            return get_template()
        if not phone.isdigit() or len(phone) != 8:
            flash('Invalid phone number!', 'warning')
            return get_template()
        else:
            phone = int(phone)
        if not check_date(birthdate):
            flash('Invalid birthdate!', 'warning')
            return get_template()
        if password != password2:
            flash('Passwords do not match!', 'warning')
            return get_template()

        awstools.createVolunteer(name, username, phone, birthdate, location, password)
        flash(f'Welcome {username}!', 'success')
        return redirect('/')
    return get_template()

