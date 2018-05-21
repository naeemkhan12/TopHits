"""
A basic starter app  with the Flask framework and PyMongo
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask.ext.login import LoginManager
from user import User
from flask_login import login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from bson.son import SON
import pprint

app = Flask(__name__)
app.config.from_object('config')
db = MongoClient().TopHits
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'



# connect to MongoDB with the defaults
#mongo    = PyMongo(app)



@app.route('/' , methods=['GET','POST'])
def home():
    if request.method == 'POST':
        users=db.users;
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
@app.route('/catalog')
def catalog():
    songs=db.songs
    filters=['energy','liveness','tempo','speechiness','Sound_quailty','instrumentalness','duration','loudness','valence','danceability','key']
    return render_template('catalog.html',elements=filters)
@app.route('/filters')
def filters():
    songs=db.songs
    filters=['energy','liveness','tempo','speechiness','Sound_quailty','instrumentalness','duration','loudness','valence','danceability','key']
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
@app.route('/filters/attributes',methods=['POST'])
def filter_on_attr():
    # app.logger.debug(request.get_json())
    content=request.get_json();
    for item in content:
        name=item['name']
        value=item['value']
        #pipeline=[{ "$project":{ "title":"$song_title",name: { "$min": [value,"$"+name] }}}, {"$sort":SON([(name,-1)])},{"$limit":5}]
    query_result=query_builder(content)
    return jsonify(query_result)

@app.route('/artists')
def get_artists():
    songs=db.songs
    query_result=songs.find().distinct('artist_name')
    return jsonify(query_result)


@app.route('/songs')
def get_singers():
    songs=db.songs
    query_result=songs.find().distinct('song_title')
    return jsonify(query_result)




def query_builder(values):
    query_values= dict()
    sort_values=[]
    query=[]
    # results= { $project:{ title:"$song_title",loudness: { $min: [-11.091,"$loudness"] },key: { $min: [5,"$key"] }}}
    # $project:{ title:"$song_title",loudness: { $min: [-11.091,"$loudness"] },key: { $min: [5,"$key"] }}
    # db.songs.aggregate([{ $project:{ title:"$song_title",loudness: { $min: [-11.091,"$loudness"] },key: { $min: [5,"$key"] }}}, {$sort:{loudness:-1,key:-1}},{$limit:5}])
    for value in values:
        if value['name']!='artist_name' and value['name']!='song_title' and value['name']!='years':
            query_values.update({value['name']: {"$min": [float(value['value']),"$"+value['name']]}})
        else:
            query_values.update({value['name']: "$"+value['name']})
            query.append({'$match':{value['name']:value['value']}})
        sort_values.append((value['name'],-1))
    query_values.update({"_id":0})
    query_values.update({"Artist Name":"$artist_name"})
    query_values.update({"Song Title":"$song_title"})
    query.append({"$project":query_values})
    query.append({"$sort":SON(sort_values)})
    query.append({"$limit":10})
    query_result=list(db.songs.aggregate(query))
    # app.logger.debug(pprint.pprint(query_result))
    # for value in query_result:
    #     app.logger.debug(value)
    #     for key in values:
    #         app.logger.debug(value[key])
    return query_result


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = db.users.find_one({"name": request.form['username']})
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
    u = db.users.find_one({"name": username})
    if not u:
        return None
    return User(u['name'])
if __name__ == '__main__':
    app.run(debug = True)
