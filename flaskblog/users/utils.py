import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    picture_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = picture_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (150,150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To Reset the password, visit the following link:
{url_for('users.password_reset', token=token, _external=True)}
If you have not request this please ignore, no change will be made
    '''
    mail.send(msg)
