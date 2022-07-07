from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def user_login():
    if request.method == 'POST':
        result = request.form
        username = result['username']
        password = result['password']
        if not username or not password:
            flash("Username and password cannot be empty!", "danger")
            return redirect("/login")
        if awstools.checkVolunteerPassword(username, password):
            awstools.login(0, username)
            flash(f"Welcome {username}!", "success")
            return redirect("/")
        flash("Invalid username or password!", "danger")
        return redirect("/login")
    return render_template('user_login.html', userinfo=awstools.getCurrentUserInfo())
