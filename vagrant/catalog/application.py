from datetime import datetime

# Flask config and intialization
from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

# Database ORM config and session creation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)

# Routing of our application
# Landing page with all categories and list of recently added Items
@app.route('/')
@app.route('/catalog/')
def landingPage():
    categories = session.query(Category).filter_by().all()
    items = session.query(Item).filter_by().order_by("timestamp desc").all()

    return render_template('landingpage.html', categories=categories, items=items)

# Show all items of a specific category
@app.route('/catalog/<string:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).filter_by().all()
    category = session.query(Category).filter_by(name=category_name).one()
    categoryitems = session.query(Item).filter_by(category_id=category.id).all()

    return render_template('category.html', categories=categories,
        category=category.name, categoryitems=categoryitems)

# Show description of a specific item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name)[0]

    return render_template('item.html', item=item)

# Add new item information after authentication
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        post_name = request.form['name']
        post_description = request.form['description']
        post_category = request.form['category']
        category = session.query(Category).filter_by(name=post_category).one()
        timestamp = unicode(datetime.now())
        newItem = Item(
            name=post_name, description=post_description,
            timestamp=timestamp, category_id=category.id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItem', category_name=category.name, item_name=newItem.name))
    else:
        categories = session.query(Category).filter_by().all()

        return render_template('newitem.html', categories=categories)

# Edit item information after authentication
@app.route('/catalog/<int:item_name>/edit/')
def editItem(item_name):
    return

# Delete item information after authentication
@app.route('/catalog/<int:item_name>/delete/')
def deleteItem(item_name):
    return

# JSON endpoint
@app.route('/catalog.json/')
def json_endpoint():
    return

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
