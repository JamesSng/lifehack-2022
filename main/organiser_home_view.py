from flask import render_template, redirect, request, flash, get_flashed_messages
import awstools

def organiser_home():
    return render_template('organiser_home.html', userinfo=awstools.getCurrentUserInfo())


