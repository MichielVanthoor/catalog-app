from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
app = Flask(__name__)

# Create session and connect to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def HelloWorld():
    categories = session.query(Category).all()
    output = ''
    for i in categories:
        output += i.name
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)