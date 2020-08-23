from flask import Flask, render_template, request, url_for, flash, redirect, Response
import sqlite3
from werkzeug.exceptions import abort
import blockchain
from camera import VideoCamera
import cv2
import pyautogui
import confirm


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hk416ak47m16'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
    

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, category, content) VALUES (?, ?, ?)', (title, category, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    return render_template('create.html')



@app.route('/userinfo', methods = ('GET','POST'))
def userinfo():
    if request.method =='POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        blockchain.automation(name, address, email)
        
        if not name:
            flash('Name is required to proceed!')
        else:
            return redirect(url_for('create'))
        
    return render_template('userinfo.html')


@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/display', methods= ['GET','POST'])
def verification():
    return render_template('verification.html')

screenshot = False
def gen(camera):
    while screenshot == False:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') 
    

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/takescreenshot', methods = ['GET','POST'])
def contact():
    if request.method == 'POST':
        if request.form['Take Photo'] == 'Take Photo':
            screenshot = True 
            myScreenshot = pyautogui.screenshot(region=(330,130, 700, 500))
            myScreenshot.save(r'./persontest.png')
            print('screenshot was taken!')
    elif request.method == 'GET':
        print("Button was not pressed")
    return render_template('verification.html')

@app.route('/comparefaces', methods = ['GET','POST'])
def comparison():
    if request.method == 'POST':
        if request.form['Verify'] == 'Verify':
            print('Id verifying...')
            confirm.check_identity()
    elif request.method == 'GET':
        print("Button was not pressed")
    
    return render_template('verification.html')

