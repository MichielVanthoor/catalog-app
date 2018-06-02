# Import dependencies for Flask, OAuth2.0 and database ORM
import httplib2
import json
import random
import requests
import string

from database_setup import Base, Category, Item, User
from datetime import datetime
from flask import Flask, render_template, request,\
  redirect, url_for, jsonify, flash, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

# Initialize Flask app and get OAuth credentials
app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Connect using Google OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code (OTP)
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                                 json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print 'In gdisconnect access token is %s' % access_token
    print 'User name & ID is: '
    print login_session['username']
    print login_session['user_id']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 100px; height: ' \
              + '100px;border-radius: 150px;-webkit-border-radius: 150px;' \
              + '-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Disconnect using Google OAuth
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s' % access_token
    print 'Disconnected user name is: '
    print login_session['username']
    requests.post('https://accounts.google.com/o/oauth2/revoke',
                  params={'token': access_token},
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})

    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    return redirect(url_for('landingPage'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Routing of our application
# Landing page with all categories and list of recently added Items
@app.route('/')
@app.route('/catalog/')
def landingPage():
    categories = session.query(Category).filter_by().all()
    items = session.query(Item).filter_by().order_by("timestamp desc").all()

    if 'username' not in login_session:
        return render_template('landingpage.html',
                               categories=categories,
                               items=items)
    else:
        return render_template('privatelandingpage.html',
                               categories=categories,
                               items=items)


# Show all items of a specific category
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).filter_by().all()
    category = session.query(Category).filter_by(name=category_name).one()
    catitems = session.query(Item).filter_by(category_id=category.id).all()

    if 'username' not in login_session:
        return render_template('category.html',
                               categories=categories,
                               category=category.name,
                               categoryitems=catitems)
    else:
        return render_template('privatecategory.html',
                               categories=categories,
                               category=category.name,
                               categoryitems=catitems)


# Show description of a specific item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name)[0]

    if 'username' not in login_session:
        return render_template('item.html', item=item)
    else:
        return render_template('privateitem.html', item=item)


# Add new item information after authentication
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        post_name = request.form['name']
        post_description = request.form['description']
        post_category = request.form['category']
        category = session.query(Category).filter_by(name=post_category).one()
        timestamp = unicode(datetime.now())
        newItem = Item(name=post_name, description=post_description,
                       timestamp=timestamp,
                       category_id=category.id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItem',
                                category_name=category.name,
                                item_name=newItem.name))
    else:
        categories = session.query(Category).filter_by().all()

        return render_template('privatenewitem.html', categories=categories)


# Edit item information after authentication
@app.route('/catalog/<string:item_name>/edit/', methods=['GET', 'POST'])
def editItem(item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    categories = session.query(Category).all()

    print item.user_id
    print login_session['user_id']

    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction()" \
                + "{window.location.href = '/catalog';" \
                + "alert('You are not authorized to edit this item." \
                + "Please create your own item in order to edit.');}" \
                + "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        post_category = request.form['category']
        category = session.query(Category).filter_by(name=post_category).one()
        item.category = category

        session.add(item)
        session.commit()
        return redirect(url_for('showItem',
                                category_name=category.name,
                                item_name=item.name))

    else:
        return render_template('privateedititem.html',
                               item=item,
                               categories=categories)


# Delete item information after authentication
@app.route('/catalog/<string:item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(item_name):
    item = session.query(Item).filter_by(name=item_name)[0]
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction()" \
                + "{window.location.href = '/catalog';" \
                + "alert('You are not authorized to delete this item." \
                + "Please create your own item in order to delete.');}" \
                + "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('landingPage'))

    else:
        return render_template('privatedeleteitem.html', item=item)


# JSON endpoint
@app.route('/catalog.json/')
def json_endpoint():
    items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
