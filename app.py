from flask import Flask,render_template,Response,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from camera import VideoCamera
from datetime import datetime
import time,os,shutil,glob


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

user_first_name=None
user_last_name=None 
user_timestamp=None


app.config['SECRET_KEY']='some_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
Migrate(app,db)


class User(db.Model):

    __tablename__='users'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    time_stamp = db.Column(db.Integer)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    path = db.Column(db.Text)

    def __init__(self,first_name,last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.time_stamp = time.time()

    def __repr__(self):
        return f"{self.id}, {self.time_stamp}, {self.first_name} {self.last_name}"


class Log(db.Model):

    __tablename__ = 'logs'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    time_stamp = db.Column(db.Integer)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    path = db.Column(db.Text)

    def __init__(self,first_name,last_name):
        self.first_name=first_name
        self.last_name=last_name
        self.time_stamp=time.time()

    def __repr__(self):
        return f"{self.id},{self.time_stamp}, {self.first_name} {self.last_name}"


db.create_all() 


video_camera = None
global_frame = None


@app.route('/')
def home_page():
	return render_template('homepage.html')

@app.route('/enroll')
def enroll_page():
    return render_template('enrollpage.html')
@app.route('/identify')
def identify_page():
    return render_template('identifypage.html')

@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera 
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record(0)
        response = jsonify(result="started")
        response.max_age=1
        return response
    else:
        video_camera.stop_record(0)
        response= jsonify(result="stopped")
        response.max_age=1
        return response

@app.route('/identify_status', methods=['POST'])
def identify_status():
    global video_camera 
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record(1)
        response = jsonify(result="started")
        response.max_age=1
        return response
    else:
        video_camera.stop_record(1)
        response= jsonify(result="stopped")
        response.max_age=1
        return response

def video_stream():
    global video_camera 
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()
        
    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/welcome')
def welcome_page():
    user_first_name = request.args.get('first')
    user_last_name = request.args.get('last')
    if(not os.path.isdir('./'+user_first_name+'_'+user_last_name)):
        os.mkdir('./'+user_first_name+'_'+user_last_name)
    new_images = glob.glob('./'+'*.png')
    for im in new_images:
        shutil.move(im,os.path.join('./'+user_first_name+'_'+user_last_name+'/'+os.path.basename(im)))
    new_user = User(user_first_name,user_last_name)
    db.session.add(new_user)
    db.session.commit()
    new_log = Log(user_first_name,user_last_name)
    db.session.add(new_log)
    db.session.commit()
    return render_template('welcome_page.html', first=user_first_name,last=user_last_name)


@app.route('/logpage')
def log_page():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_ts = datetime.timestamp(datetime.strptime(start_date,'%d-%m-%Y')) 
    end_ts = datetime.timestamp(datetime.strptime(end_date,'%d-%m-%Y'))
    all_users = Log.query.filter(Log.time_stamp>=start_ts,Log.time_stamp<=end_ts)
    return render_template('logpage.html',list=all_users)


if (__name__=='__main__'):
	app.run(threaded=True)
