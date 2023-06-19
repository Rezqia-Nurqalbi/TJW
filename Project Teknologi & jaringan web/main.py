from flask import Flask, render_template, request, redirect
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.debug = True

# Scene 1: Login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sender = request.form['email']
        password = request.form['password']
        receiver = request.form['receiver']
        subject = request.form['subject']
        message = request.form['message']

        send_email(sender, password, receiver, subject, message)

        return 'Email sent successfully.'
    else:
        return render_template('login.html')


@app.route('/start', methods=['POST'])
def start():
    return render_template('index.html')

# Scene 2: Email Form
@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        emails = read_emails(username, password)
        return render_template('emails.html', emails=emails)
    else:
        return render_template('inbox.html')

@app.route('/reply', methods=['POST'])
def reply():
    # Mendapatkan data dari form
    sender = request.form['email']
    password = request.form['password']
    receiver = request.form['receiver']
    subject = request.form['subject']
    message = request.form['message']

    # Mengirim email
    send_email(sender, password, receiver, subject, message)

    return 'Email sent successfully.'

def send_email(sender, password, receiver, subject, message):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

def read_emails(username, password):
    with imaplib.IMAP4_SSL('imap.gmail.com', 993) as server:
        server.login(username, password)
        server.select('INBOX')
        _, data = server.search(None, 'ALL')
        email_ids = data[0].split()[-10:]

        emails = []
        for email_id in email_ids:
            _, email_data = server.fetch(email_id, '(RFC822)')
            raw_email = email_data[0][1]
            msg = email.message_from_bytes(raw_email)
            email_info = {
                'from': msg['From'],
                'subject': msg['Subject'],
                'message': extract_message(msg),  # Menggunakan fungsi extract_message()
                'date': msg['Date']
            }
            emails.append(email_info)

        return emails

def extract_message(msg):
    if msg.is_multipart():
        # Jika pesan adalah pesan multipart, cari bagian teks biasa
        for part in msg.get_payload():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()
    else:
        # Jika pesan bukan pesan multipart, langsung kembalikan isi pesan
        return msg.get_payload()

if __name__ == '__main__':
    app.run()
