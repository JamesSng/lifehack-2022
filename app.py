from flask import Flask, render_template, url_for, redirect
from main import user_login_view, organiser_login_view, user_register_view, organiser_register_view, user_profile_view, user_home_view, organiser_home_view
import awstools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sadfaces218'

@app.route('/')
def home():
    info = awstools.getCurrentUserInfo()
    if info == None or info['usertype'] == 0:
        return redirect('/user_home')
    else:
        return redirect('/organiser_home')
    return render_template('base.html', userinfo=awstools.getCurrentUserInfo())

@app.route('/logout')
def logout():
    awstools.logout()
    return redirect('/')

app.add_url_rule('/login', view_func = user_login_view.user_login, methods = ['GET', 'POST'])
app.add_url_rule('/org_login', view_func = organiser_login_view.organiser_login, methods = ['GET', 'POST'])
app.add_url_rule('/register', view_func = user_register_view.user_register, methods = ['GET', 'POST'])
app.add_url_rule('/org_register', view_func = organiser_register_view.organiser_register, methods = ['GET', 'POST'])
app.add_url_rule('/user_profile', view_func = user_profile_view.user_profile)
app.add_url_rule('/user_home', view_func = user_home_view.user_home)
app.add_url_rule('/organiser_home', view_func = organiser_home_view.organiser_home)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=80, debug=True)
