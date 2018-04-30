"""
A basic starter app  with the Flask framework and PyMongo
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_pymongo import PyMongo


app = Flask(__name__)

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT']='27017'
app.config['MONGO_DBNAME']="TopHits"

# connect to MongoDB with the defaults
#mongo    = PyMongo(app)

mongo = PyMongo(app,config_prefix='MONGO')




@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def aboutUs():
    return render_template("about.html")


@app.route('/contact')
def getcontactUs():
    return render_template("contactus.html")

if __name__ == '__main__':
    app.run(debug = True)
