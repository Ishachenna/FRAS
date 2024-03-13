from flask import Flask, render_template, request, redirect, url_for, Response,flash
import cv2
import firebase_admin
from firebase_admin import credentials, auth, db,firestore,storage
import os
# cred = credentials.Certificate("E:/my_studies/Majorproject/majorproject-550be-firebase-adminsdk-wzfdz-4b636ba1b9.json")
# firebase_admin.initialize_app(cred,{
#     'databaseURL':'https://majorproject-550be-default-rtdb.firebaseio.com/'
# })

cred = credentials.Certificate("E:/my_studies/Majorproject/majorproject-550be-firebase-adminsdk-wzfdz-4b636ba1b9.json")
firebase_admin.initialize_app(cred,{
    'storageBucket':'majorproject-550be.appspot.com'
})
db=firestore.client()
bucket = storage.bucket()
app = Flask(__name__,template_folder="E:/my_studies/Majorproject")
app.secret_key = 'Monu@143'
camera = cv2.VideoCapture(0)  # Initialize webcam

# Dummy data for students and admins (in real-world scenarios, this data would be stored in a database)
students = []
admins = [{'username': 'admin', 'password': 'admin'}]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # ref=db.reference('/student')
   
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usn=request.form['usn']
        sem=request.form['sem']
        branch=request.form['branch']
        status='pending'
        # Add the student to the list of pending students (to be approved by admin)
        print(username)
        print(password)
#         ref.set({
#     'name': username,
#     'password': password,
#     # Add more key-value pairs as needed
# })
        d={'name':username,'password':password,'usn':usn,'sem':sem,'branch':branch,'status':status}
            # db.collection('student').add(d)
        db.collection('student').document(usn).set(d)
        students.append({'username': username, 'password': password, 'approved': False})
        capture_images(usn)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the admin credentials are correct
        if {'username': username, 'password': password} in admins:
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error=True)
    return render_template('admin_login.html', error=False)


@app.route('/admin/dashboard')
def admin_dashboard():
    # return render_template('admin_dashboard.html', students=students)
     pending_students = db.collection('student').where('status', '==', 'pending').stream()
     return render_template('admin_dashboard.html', pending_students=pending_students)


# @app.route('/admin/approve/<usn>')
# def approve_student(usn):
#      db.collection('students').document(usn).update({'status': 'approved'})
#      flash('Student approved successfully.')
#     # Find the student by username and approve them
#     #  for student in students:
#     #     if student['username'] == username:
#     #         student['approved'] = True
#     #         break
#      return redirect(url_for('admin_dashboard'))

@app.route('/approve/<usn>')
def approve(usn):
    # Update student status to 'approved'
    db.collection('student').document(usn).update({'status': 'approved'})
    flash(f'Registration request for USN {usn} has been approved.')
    return redirect(url_for('admin_dashboard'))


# def detect_faces(frame):
#     ref=db.reference('/student')
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
#         # Capture and store the detected face
#         detected_face = frame[y:y+h, x:x+w]
#         ref.push(detected_face.tolist())  # Convert numpy array to list before storing
#     return frame

def detect_faces(frame):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    for (x, y, w, h) in faces:
        print(x)
        print(y)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return frame

def capture_images(usn, num_samples=10):
    camera = cv2.VideoCapture(0)
    face_dir = f'faces/{usn}'
    os.makedirs(face_dir, exist_ok=True)
    count = 0
    while count < num_samples:
        success, frame = camera.read()
        if not success:
            continue
        frame = detect_faces(frame)
        face_path = f'{face_dir}/face_{count}.jpg'
        cv2.imwrite(face_path, frame)
        # upload_to_firebase(face_path)
        blob = bucket.blob(face_path)   # Specify the path to store the image in Firebase Storage
        blob.upload_from_filename(face_path)
        count += 1
    camera.release()


# def upload_to_firebase(image_path):
#     # blob = bucket.blob(image_path)
#     # blob.upload_from_filename(image_path)
#      filename = os.path.basename(image_path)  # Extract filename from full path
#      blob = bucket.blob(filename)
#      blob.upload_from_filename(image_path)
# def upload_to_firebase(image_path):
#     filename = os.path.basename(image_path)  # Extract filename from full path
#     blob = bucket.blob(f'faces/{filename}')   # Specify the path to store the image in Firebase Storage
#     blob.upload_from_filename(image_path)

    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # return frame

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = detect_faces(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
# app.py
# from flask import Flask, render_template, Response
# import cv2

# app = Flask(__name__,template_folder="E:/my_studies/Majorproject")
# camera = cv2.VideoCapture(0)  # Initialize webcam

# def detect_faces(frame):
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
#     return frame

# def generate_frames():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             frame = detect_faces(frame)
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True)
