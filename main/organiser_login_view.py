from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def organiser_login():
    if request.method == 'POST':
        result = request.form
        username = result['username']
        password = result['password']
        if awstools.checkOrganiserPassword(username, password):
            awstools.login(1, username)
            flash(f"Welcome {username}!", "success")
            return redirect("/")
        flash("Invalid username or password!", "danger")
        return redirect("/org_login")
    return render_template('organiser_login.html', userinfo=awstools.getCurrentUserInfo())

