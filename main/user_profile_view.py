from flask import render_template, redirect, request
import awstools

def user_profile():
    return render_template('user_profile.html', userinfo=awstools.getCurrentUserInfo(), profileinfo=awstools.getCurrentUserInfo())

