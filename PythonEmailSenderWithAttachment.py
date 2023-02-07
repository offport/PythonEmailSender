import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from email.mime.application import MIMEApplication
from flask import Flask, request, render_template

app = Flask(__name__)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'password'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Determines if the basic auth is required"""
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET', 'POST'])
@requires_auth
def send_email():
    if request.method == 'POST':
        sender = request.form['sender']
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']
        file = request.files.get('attachment')
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body))

            if file:
                file_name = file.filename
                with open(file_name, 'rb') as f:
                    file_data = f.read()
                file_attachment = MIMEApplication(file_data, Name=file_name)
                file_attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
                msg.attach(file_attachment)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login("mail@gmail.com", "password")
            server.send_message(msg)
            server.quit()
            return "Email sent successfully"
        except Exception as e:
            return "Error: {}".format(str(e))
    return render_template('index2.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return "file uploaded successfully. Please go back and send the email."
    
if __name__ == '__main__':
    app.run()

    
