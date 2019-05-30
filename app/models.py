from app import db

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id'))
                           )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))
    about_me = db.Column(db.String(1000))
    about_you = db.Column(db.String(1000))


class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))

    def __repr__(self):
        return '<Interest {}>'.format(self.text)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Связь один-ко-многим с таблицей User
    user = db.relationship('User', backref=db.backref('photos', lazy=True))
