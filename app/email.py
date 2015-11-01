from flask.ext.mail import Message
from flask import current_app, render_template
from . import mail


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['APP_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['APP_MAIL_SENDER'], recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
