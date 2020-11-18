from app import db

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id')))

# таблица для отслеживания кому чья анкета была показана
show_profile = db.Table('show_profile',
                        # кто видел анкету пользователя
                        db.Column('showed_profile_id', db.Integer, db.ForeignKey('user.id')),
                        # чью анкету увидел пользователь
                        db.Column('sight_profile_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))
    about_me = db.Column(db.String(1000))
    sexual_preferences = db.Column(db.String(7), default='all')  # анкеты какого гендера показывать пользователю: male, female или all
    sight_profiles = db.relationship('User', secondary=show_profile, primaryjoin=(show_profile.c.showed_profile_id == id),
                                     secondaryjoin=(show_profile.c.sight_profile_id == id),
                                     backref=db.backref('showed_profile_id', lazy='dynamic'), lazy='dynamic')


class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))

    def __repr__(self):
        return '<Interest {}>'.format(self.text)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Связь один-ко-многим с таблицей User
    user = db.relationship('User', backref=db.backref('photos', lazy=True))
