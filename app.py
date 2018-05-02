"""
A basic starter app  with the Flask framework and PyMongo
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask.ext.login import LoginManager
from user import User
from flask_login import login_user, logout_user, login_required, current_user
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object('config')
mongo = PyMongo(app,config_prefix='MONGO')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'



# connect to MongoDB with the defaults
#mongo    = PyMongo(app)



@app.route('/' , methods=['GET','POST'])
def home():
    if request.method == 'POST':
        users=mongo.db.users;
        existing_user = users.find_one({'name': request.form['username']})
        if existing_user is None:
            password = request.form['password']
            password=generate_password_hash(password, method='pbkdf2:sha256')
            users.insert_one({'name': request.form['username'], 'password': password})
            return redirect(url_for('profile'))
        flash ('Seems like you  already have an account',category="info")
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/about')
def aboutUs():
    return render_template("about.html")

@app.route('/profile')
def profile():
    return render_template('profile.html')
@app.route('/contact')
def getcontactUs():
    return render_template("contactus.html")
@app.route('/catalog')
def catalog():
    songs=mongo.db.songs
    filters=['energy','liveness','tempo','speechiness','Sound_quailty','instrumentalness','duration','loudness','valence','danceability']
    elements=[]
    for attr in filters:
        max_value=songs.find({},{attr:1,"_id":0}).sort("loudness",1).limit(1)
        min_value=songs.find({},{attr:1,"_id":0}).sort("loudness",-1).limit(1)
        elem = {
            'name':attr,
            'max': max_value[0][attr],
            'min': min_value[0][attr]
        }
        elements.append(elem)
    return render_template('catalog.html',elements=elements)
@app.route('/filters')
def filters():
    songs=mongo.db.songs
    filters=['energy','liveness','tempo','speechiness','Sound_quailty','instrumentalness','duration','loudness','valence','danceability']
    elements=[]
    for attr in filters:
        max_value=songs.find({attr:{"$ne" :"NULL"}}).sort(attr,-1).limit(1)
        min_value=songs.find({attr:{"$ne" :"NULL"}}).sort(attr,1).limit(1)
        elem = {
            'name':attr,
            'max': max_value[0][attr],
            'min': min_value[0][attr]
        }
        elements.append(elem)
    return jsonify(elements)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.username is not None:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        user = mongo.db.users.find_one({"name": request.form['username']})
        if user and User.validate_login(user['password'], request.form['password']):
            user_obj = User(user['name'])
            login_user(user_obj)
            return redirect(request.args.get("next") or url_for("home"))
        flash ('Invalid Username or Password',category="danger")
    return render_template('login-page.html', title='login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@lm.user_loader
def load_user(username):
    u = mongo.db.users.find_one({"name": username})
    if not u:
        return None
    return User(u['name'])
if __name__ == '__main__':
    app.run(debug = True)
