# Flask config and intialization
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

# Database ORM config and session creation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Routing of our application
# Landing page with all categories and list of recently added Items
@app.route('/')
@app.route('/catalog/')
def landingPage():
    categories = session.query(Category).all()

    return render_template('categories.html', categories=categories)

# Show all items of a specific categloy
@app.route('/catalog/<int:category_name>/items/')
def showCategory(category_name):
    return

# Show description of a specific item
@app.route('/catalog/<int:category_name>/<int:item_name>/')
def showItem(category_name, item_name):
    return

# Add new item information after authentication
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        post_name = request.form['name']
        post_description = request.form['description']
        post_category = request.form['category']
        #TODO: built in a way to get foreign key
        newItem = Item(
            name=post_name, description=post_description, category=post_category)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItem', category_name=category_name, item_name=item_name))
    else:
        categories = session.query(Category).all()

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
