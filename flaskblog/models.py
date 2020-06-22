from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db,login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    email = db.Column(db.String(50),nullable=False,unique=True)
    profile_pic = db.Column(db.String, default='default.jpg')
    password = db.Column(db.String,nullable=False)
    posts = db.relationship('Post',backref='author',lazy=True)

    def get_reset_token(self, expiration_time=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration_time)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def validate_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'{self.username}, {self.email}, {self.profile_pic},{self.password}'


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content = db.Column(db.String(500),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f'{self.title}, {self.content}'

