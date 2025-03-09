import smtplib
from flask import Flask, request, render_template, Response
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

app = Flask(__name__)

# Authentication function
def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == 'admin' and password == 'password'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

# Decorator for authentication
def requires_auth(f):
    """Determines if basic auth is required"""
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
        sender = request.form['sender']  # Spoofed sender
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']
        file = request.files.get('attachment')

        try:
            # Construct the email
            msg = MIMEMultipart()
            msg['Reply-To'] = sender  # Sets the spoofed sender
            msg['From'] = smtp_user  # Must match the authenticated SMTP user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Handle file attachment
            if file and file.filename:
                file_data = file.read()
                file_attachment = MIMEApplication(file_data, Name=file.filename)
                file_attachment['Content-Disposition'] = f'attachment; filename="{file.filename}"'
                msg.attach(file_attachment)

            # SMTP server settings (modify accordingly)
            smtp_server = "smtp.gmail.com"  # Change if using another provider
            smtp_port = 587
            smtp_user = "email@gmail.com"  # Change to your email CHANGE ME!!<<<<<<<<<<<<<<<<<<<<<
            smtp_pass = "password"  # Use App Passwords for Gmail CHANGE ME!!<<<<<<<<<<<<<<<<<<<<<

            # Sending the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(sender, recipient, msg.as_string())
            server.quit()

            return "Email sent successfully with attachment!"
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
