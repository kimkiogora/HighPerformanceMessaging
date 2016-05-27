# Author    kim kiogora <kimkiogora@gmail.com>
# Usage     Web Portal for viewing activity
# Version   1.0
# Since     23 March 2016


# import the Flask class from the flask module
import MySQLdb, os, time
from flask import Flask, current_app, Response, session, url_for, render_template, redirect, request

# create the application object
app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


"""
Verify user is who (s)he says
"""

def check_session(user, pwd):
    _login = {}
    db = MySQLdb.connect(host=app.config['db_server'],
                         user=app.config['db_user'],
                         passwd=app.config['db_password'],
                         db=app.config['db_name'])
    cur = db.cursor()
    cur.execute("select userID, sessionID, status from users where username = '%s' and password = md5('%s')"
                " and status='active'" % (user, pwd))
    data = cur.fetchone()

    if data is not None:
        if data[0] is not None:
            _login['verified'] = True
            if data[1] is not None:
                _login['has_session_id'] = "yes"
            else:
                _login['has_session_id'] = "no"
                #_login['reason'] = "User is ".join(str(data[3]))
        else:
            _login['verified'] = False
            _login['has_session_id'] = "no"
    else:
        _login['verified'] = False
        _login['has_session_id'] = "no"

    db.close()
    return _login


@app.route('/login', methods=['POST', 'GET'])
def login():
    data = {}

    db = MySQLdb.connect(host=app.config['db_server'],
                         user=app.config['db_user'],
                         passwd=app.config['db_password'],
                         db=app.config['db_name'])
    cur = db.cursor()

    if request.method == 'POST':
        data[0] = request.form['username']
        data[1] = request.form['password']

        login_data = check_session(data[0], data[1])
        if str(login_data['verified']) is 'False':
            return render_template('index.html', error="Invalid username/password provided")

        # Update sessionID
        cur.execute("update users set sessionID = '%s' where username='%s' and password=md5('%s')"
                    % (str(time.time()), data[0], data[1]))
        db.commit()
        # Save sessionID

        session['username'] = data[0]
        session['password'] = data[1]
    else:
        if 'username' in session and 'password' in session:
            login_data = check_session(session['username'], session['password'])
            if 'yes' == str(login_data['has_session_id']):
                data[0] = session['username']
                data[1] = session['password']
            else:
                return render_template('index.html', error="Invalid username/password provided")
        else:
            return render_template('index.html')

    #Get & render data

    db.close()
    return render_template('main.html', data=data)


@app.route('/logout', methods=['GET'])
def logout():
    if "username" in session:
        db = MySQLdb.connect(host=app.config['db_server'],
                             user=app.config['db_user'],
                             passwd=app.config['db_password'],
                             db=app.config['db_name'])
        cur = db.cursor()
        cur.execute("update users set sessionID=NULL where username='%s' and password=md5('%s')"
                    % (session['username'], session['password']))
        db.commit()
        db.close()

        session.pop('username', None)
        session.pop('password', None)
        session.pop('session_id', None)
        session.modified = True
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')  # render a template

@app.route('/create_account', methods=['GET'])
def create_account():
    return render_template('index.html')  # render a template


# use decorators to link the function to a url
@app.route('/')
def home():
    return redirect(app.config['home_url'])

# start the server with the 'run()' method
if __name__ == '__main__':
    app.secret_key = "somesecretkeyishere!23"

    # Configurations
    s_port = 8085

    app.config['app_name'] = "Bulk Messaging, BP"
    app.config['db_server'] = "localhost"
    app.config['db_user'] = ""
    app.config['db_password'] = ""
    app.config['db_name'] = "bulksms"
    app.config['home_url'] = ("http://localhost:%d/index" % s_port)

    # run
    app.run(host='0.0.0.0', port=s_port, debug=True)
