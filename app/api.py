from flask_restful import reqparse, abort, Api, Resource
from app import app, db
from app.models import User, Interests, Photo
from flask import jsonify, request, make_response
import time
import werkzeug

api = Api(app)

SECRET_PASSWORD = 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'


def type_error(field, type_field):
    return {'error': 'An error occurred. ' + field[0].upper() + field[1:] + ' must be only str, not ' + type_field}


# Аборты
def abort_if_user_not_found(id):
    if User.query.filter_by(telegram_id=id).first() is None:
        abort(404, message="User {} not found".format(id))


def abort_if_password_false(password):
    if password != SECRET_PASSWORD:
        abort(400, message='Access error')


def abort_if_user_found(id):
    if User.query.filter_by(telegram_id=id).first() is not None:
        abort(404, message="User {} already exist".format(id))


# Запрет абортов


class UserApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=False)
    parser.add_argument('gender', required=False)
    parser.add_argument('age', required=False)
    parser.add_argument('interests', required=False)
    parser.add_argument('about_me', required=False)

    def delete(self, user_id):
        try:
            if 'password' not in request.headers:
                abort(400, message='Access error')
            abort_if_password_false(request.headers['password'])

            abort_if_user_not_found(user_id)
            user = User.query.filter_by(telegram_id=user_id).first()

            user.photos = []
            db.session.commit()
            return jsonify({'status': 'OK', 'message': 'All photos were deleted'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'An error occurred'})

    def get(self, user_id):
        # Не зная пароль никто не сможет получить данные пользователей
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])

        abort_if_user_not_found(user_id)
        user = User.query.filter_by(telegram_id=user_id).first()
        result = {
            'name': user.name,
            'gender': user.gender,
            'age': str(user.age),
            'count_photos': str(len(user.photos)),
            'telegram_id': str(user.telegram_id),
            'about_me': user.about_me,
            'interests': ','.join([text.text for text in user.interests]),
        }
        return jsonify({'user': result})

    def put(self, user_id):
        # Не зная пароль никто не сможет изменить данные пользователей
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])

        args = self.parser.parse_args()
        abort_if_user_not_found(user_id)

        user = User.query.filter_by(telegram_id=user_id).first()
        if list(request.files):
            photo = Photo(image=request.files['file'].read())
            db.session.add(photo)
            user.photos.append(photo)
            db.session.commit()
        try:
            if args['name'] is not None:
                if len(args['name']) > 200:
                    return jsonify({'error': 'Max length of name is 200 symbols'})
                user.name = args['name']
                db.session.commit()

            if args['gender'] is not None:
                try:
                    genderr = str(args['gender'])
                    if genderr not in ['male', 'female']:
                        return jsonify({'error': 'Incorrect value. Available only "male" and "female"'})
                except Exception as e:
                    return jsonify(type_error('gender', str(type(args['gender']))))
                user.gender = genderr
                db.session.commit()

            if args['age'] is not None:
                try:
                    agee = int(args['age'])
                except Exception as e:
                    return jsonify({'error': 'Age can only contain numbers'})
                user.age = agee
                db.session.commit()

            if args['interests'] is not None:
                try:
                    user.interests = []
                    db.session.commit()
                    interestss = args['interests'].split(',')
                    for i in range(len(interestss)):
                        interestss[i] = interestss[i].lower().lstrip().rstrip()
                        if len(interestss[i]) > 256:
                            return jsonify({'error': 'Length one of the interests more than 256'})
                        if Interests.query.filter_by(text=interestss[i]).first() is None:
                            db.session.add(Interests(text=interestss[i]))
                            db.session.commit()
                        if Interests.query.filter_by(text=interestss[i]).first() not in user.interests:
                            user.interests.append(Interests.query.filter_by(text=interestss[i]).first())
                    db.session.commit()
                except Exception as e:
                    return jsonify({'error': 'An error occurred'})

            if args['about_me'] is not None:
                try:
                    about_mee = str(args['about_me'])
                    if len(about_mee) > 1000:
                        return jsonify({'error': 'maximum about_me length - 1000 symbols'})
                except Exception as e:
                    return jsonify(type_error('about_me', str(type(args['about_me']))))
                user.about_me = about_mee
                db.session.commit()

            return jsonify({'success': 'Ok'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'})


class UserExist(Resource):
    def get(self, user_id):
        # Не зная пароль никто не сможет получить данные пользователей
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])
        abort_if_user_not_found(user_id)
        return jsonify({'success': 'OK'})


class UserPhotos(Resource):
    parser = reqparse.RequestParser()
    # number_photo - это номер фотографии, которую мы хотим получить. Т.к. нельзя отправить сразу несколько фотографий,
    # приходится отправлять по одной
    parser.add_argument('number_photo', required=True)

    def get(self, user_id):
        # Не зная пароль никто не сможет получить данные пользователей
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])
        abort_if_user_not_found(user_id)

        args = self.parser.parse_args()
        try:
            photo = User.query.filter_by(telegram_id=user_id).first().photos[int(args['number_photo'])].image
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'photo number {} not found'.format(args['number_photo'])})
        response = make_response(photo)
        response.headers['content-type'] = 'application/octet-stream'
        return response


class UserSearch(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('telegram_id')

    def post(self):
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])
        args = self.parser.parse_args()
        try:
            telegram_id = int(args['telegram_id'])
        except Exception as e:
            return jsonify({'error': 'telegram_id can only contain numbers'})

        abort_if_user_not_found(telegram_id)

        user = User.query.filter_by(telegram_id=telegram_id).first()
        users_with_common_interests = set()  # множество пользователей, с которыми совпали интересы
        for interest in user.interests:
            for us in interest.users:
                if us.id != user.id and us not in user.sight_profiles and (
                        us.gender == user.sexual_preferences or user.sexual_preferences == 'all'):
                    users_with_common_interests.add(us)

        # сортируем пользователей по совпадениям интересов с исходным пользователем
        users_with_common_interests = sorted(users_with_common_interests, key=lambda usr: set(usr.interests) & set(user.interests))
        if users_with_common_interests:  # если такой пользователь есть
            users_with_common_interests = users_with_common_interests[-1]
        else:
            for us in User.query.all():  # если нет то берем первого попавшегося
                if us not in user.sight_profiles and us.id != user.id:
                    users_with_common_interests = us
                    break
            if not users_with_common_interests:  # если мы показали пользователю все возможные анкеты
                return jsonify({'status': 'error', 'message': 'there are no suitable profiles for this user'})

        user.sight_profiles.append(users_with_common_interests)
        db.session.commit()
        return jsonify({'status': 'OK', 'telegram_id_suitable_profile': users_with_common_interests.telegram_id})


class UserListApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('gender', required=True)
    parser.add_argument('age', required=True)
    parser.add_argument('interests', required=True)
    parser.add_argument('about_me', required=True)
    parser.add_argument('telegram_id', required=True)

    def post(self):
        # Не зная пароль, никто не сможет добавить пользователя
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])

        args = self.parser.parse_args()

        # Проверка телеграм-айди
        try:
            telegram_id = int(args['telegram_id'])
        except Exception as e:
            return jsonify({'error': 'Telegram_id can only contain numbers'})

        abort_if_user_found(args['telegram_id'])

        # Проверка имени пользователя
        try:
            name = str(args['name'])
            if len(name) > 200:
                return jsonify({'error': 'Max length of name is 200 symbols'})
        except Exception as e:
            return jsonify(type_error('name', str(type(args['name']))))

        # Проверка возраста
        try:
            age = int(args['age'])
        except Exception as e:
            return jsonify({'error': 'Age can only contain numbers'})

        # Проверка гендера пользователя
        try:
            gender = str(args['gender'])
            if gender not in ['male', 'female']:
                return jsonify({'error': 'Incorrect value. Available only "male" and "female"'})
        except Exception as e:
            return jsonify(type_error('gender', str(type(args['gender']))))

        # Проверка информации о пользователе
        try:
            about_me = str(args['about_me'])
            if len(about_me) > 1000:
                return jsonify({'error': 'maximum about_me length - 1000 symbols'})
        except Exception as e:
            return jsonify(type_error('about_me', str(type(args['about_me']))))

        user = User(name=name, gender=gender, age=age, about_me=about_me, about_you=about_you, telegram_id=telegram_id)
        # Добавление интересов для пользователя
        try:
            interestss = args['interests'].split(',')
            for i in range(len(interestss)):
                interestss[i] = interestss[i].lower().lstrip().rstrip()
                if len(interestss[i]) > 256:
                    return jsonify({'error': 'Length one of the interests more than 256'})
                if Interests.query.filter_by(text=interestss[i]).first() is None:
                    db.session.add(Interests(text=interestss[i]))
                    db.session.commit()
                if Interests.query.filter_by(text=interestss[i]).first() not in user.interests:
                    user.interests.append(Interests.query.filter_by(text=interestss[i]).first())
                db.session.commit()
        except Exception as e:
            return jsonify({'error': 'An error occurred'})
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': 'Ok'})


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserExist, '/api/user_exist/<int:user_id>')
api.add_resource(UserPhotos, '/api/user_photos/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
api.add_resource(UserSearch, '/api/search_profile')
