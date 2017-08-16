from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(24))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))
    last_post = db.Column(db.Integer)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    messagess = db.relationship('Message', backref='authorhandle',
                                lazy='dynamic')

    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Post(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.content)


class Message(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String)
    content = db.Column(db.String)
    pub_date = db.Column(db.DateTime)
    recipient = db.Column(db.String)
    author = db.Column(db.String, db.ForeignKey('user.handle'))
    read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Message %r>' % (self.content)
