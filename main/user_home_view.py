from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def user_home():
    return render_template('user_home.html', userinfo=awstools.getCurrentUserInfo())

