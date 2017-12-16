from flask import Flask, render_template, request, redirect, jsonify, g
from flask import url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import os


app = Flask(__name__)
app.secret_key = '20kuN!'

# Retrieves client ID's and secrets from the json files
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CLIENT_ID = json.loads(open(BASE_DIR + '/client_secrets.json', 'r')
                       .read())['web']['client_id']
APP_ID = json.loads(open(BASE_DIR + '/fb_client_secrets.json', 'r')
                    .read())['web']['app_id']
APP_SECRET = json.loads(open(BASE_DIR + '/fb_client_secrets.json', 'r')
                        .read())['web']['app_secret']

# Connect to Database and create database session
engine = create_engine('postgresql://postgres:1qaz!QAZ@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login handler
@app.route('/login')
def showLogin():
    """JSON API to view entire catalog Information."""
    return render_template('login.html')


# Third Party Oauth callback
@app.route('/oauth/<provider>', methods=['POST'])
def oauthLogin(provider):
    """
    Retrieves provider to process oauth login.
    params:(string) oauth provider
    """
    if provider == 'google':
        code = request.data
        try:
            # Upgrade auth code into credentials object
            oauth_flow = flow_from_clientsecrets(BASE_DIR + '/client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Check for valid access token
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?' \
              'access_token={}'.format(access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # Access token error handling
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = ' application/json'
            return response

        # Store access token in session
        login_session['provider'] = 'google'
        login_session['access_token'] = access_token
        login_session['gplus_id'] = credentials.id_token['sub']

        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': login_session['access_token'], 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

    elif provider == 'facebook':
        access_token = request.data
        url = 'https://graph.facebook.com/oauth/access_token?grant_type=' \
        'fb_exchange_token&client_id={}&client_secret={}&' \
        'fb_exchange_token={}'.format(APP_ID, APP_SECRET, access_token)  # noqa
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # Strip expire tag from access token
        access_token = result['access_token']

        url = 'https://graph.facebook.com/v2.11/me?access_token={}&fields=' \
        'name,id,email,picture'.format(access_token)  # noqa
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # Get user info
        data = result

        login_session['access_token'] = access_token
        login_session['provider'] = 'facebook'
        login_session['username'] = data['name']
        login_session['email'] = data['email']
        login_session['picture'] = data['picture']['data']['url']
        login_session['facebook_id'] = data['id']

    # Checks if user exists in DB
    if getUserID(login_session['email']) is not None:
        login_session['user_id'] = getUserID(login_session['email'])
    else:
        createUser(login_session)
        login_session['user_id'] = getUserID(login_session['email'])

    # Stores token in session
    user = session.query(User).filter_by(email=login_session['email']).first()
    token = user.generate_auth_token(600)
    login_session['token'] = token

    output = ''
    output += '<h1>Welcome, {}!</h1>'.format(login_session['username'])
    output += '<img src="{}" '.format(login_session['picture'])
    output += 'style = "width: 300px; height: 300px; border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash('Now logged in as {}'.format(login_session['username']))
    return output


def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Revoke current user's token and reset login_session
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['token']
        flash("You have been successfully logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("No user has been logged in.")
        return redirect(url_for('showCatalog'))


# JSON APIs to view Category Information.
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.category_id).limit(3)

    return jsonify(Categories=[c.serialize for c in categories],
                   Items=[i.serialize for i in items])


@app.route('/catalog/<category>/JSON')
def catalogCategoryJSON(category):
    itemCategory = session.query(Category).filter_by(name=category).first()
    items = session.query(Item).filter_by(category_id=itemCategory.id).all()

    return jsonify(Categories=[itemCategory.serialize],
                   Items=[i.serialize for i in items])


@app.route('/catalog/<category>/<item>/JSON')
def categoryItemJSON(category, item):
    itemCategory = session.query(Category).filter_by(name=category).first()
    item = session.query(Item).filter_by(name=item,
                                         category_id=itemCategory.id).first()

    return jsonify(Category=[itemCategory.serialize],
                   Item=[item.serialize])


# Show all Categories and the latest items
@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.category_id).limit(3)
    if 'token' not in login_session:
        return render_template('publiccatalog.html',
                               categories=categories, items=items)
    else:
        return render_template('catalog.html',
                               categories=categories, items=items)


# Show Items in a category item
@app.route('/catalog/<category>/')
def showCatalogCategory(category):
    itemCategory = session.query(Category).filter_by(name=category).first()
    items = session.query(Item).filter_by(category_id=itemCategory.id).all()
    categories = session.query(Category).all()
    if 'token' not in login_session:
        return render_template('publiccategory.html',
                               items=items, category=itemCategory,
                               categories=categories)
    else:
        return render_template('category.html', items=items,
                               category=itemCategory, categories=categories)


# Show an item in a category
@app.route('/catalog/<category>/<item>/')
def showCategoryItem(category, item):
    category = session.query(Category).filter_by(name=category).first()
    item = session.query(Item).filter_by(name=item,
                                         category_id=category.id).first()
    categories = session.query(Category).all()
    if 'token' not in login_session:
        return render_template('publiccategoryitem.html',
                               item=item, category=category,
                               categories=categories)
    return render_template('categoryitem.html', item=item,
                           category=category, categories=categories)


# Create a new item
@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategoryItem():
    if 'token' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).first()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category.id, user_id=user.id)
        session.add(newItem)
        session.commit()
        flash('New Item {} Successfully Added'.format(newItem.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newcategoryitem.html', categories=categories)


# Edit a category item
@app.route('/catalog/<category>/<item>/edit', methods=['GET', 'POST'])
def editCategoryItem(category, item):
    if 'token' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).first()
    categoryItem = session.query(Category).filter_by(name=category).first()
    editedItem = session.query(Item).filter_by(
        name=item, category_id=categoryItem.id).first()
    categories = session.query(Category).all()
    if user.id != editedItem.user_id:
        flash('You are not authorized to edit {}.'.format(item))
        return redirect(url_for('showCategoryItem', category=categoryItem.name,
                                item=editedItem.name))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            category = session.query(Category).filter_by(
                name=request.form['category']).first()
            editedItem.category_id = category.id
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategoryItem',
                                category=request.form['category'],
                                item=editedItem.name))
    else:
        return render_template('editcategoryitem.html',
                               category=categoryItem.name,
                               item=editedItem.name, categories=categories,
                               editedItem=editedItem)


# Delete a category item
@app.route('/catalog/<category>/<item>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category, item):
    if 'token' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).first()
    categoryItem = session.query(Category).filter_by(name=category).first()
    itemToDelete = session.query(Item).filter_by(
        name=item, category_id=categoryItem.id).first()
    if user.id != itemToDelete.user_id:
        flash('You are not authorized to delete {}.'.format(item))
        return redirect(url_for('showCategoryItem', category=categoryItem.name,
                                item=itemToDelete.name))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletecategoryitem.html',
                               category=categoryItem.name,
                               item=itemToDelete.name)


if __name__ == '__main__':
    app.debug = True
    app.run()
