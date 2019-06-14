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
    parser.add_argument('about_you', required=False)

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
            'about_me': user.about_me,
            'about_you': user.about_you,
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

            if args['about_you'] is not None:
                # Проверка информации о собеседнике
                try:
                    about_youu = str(args['about_you'])
                    if len(about_youu) > 1000:
                        return jsonify({'error': 'maximum about_you length - 1000 symbols'})
                except Exception as e:
                    return jsonify(type_error('about_you', str(type(args['about_you']))))
                user.about_you = about_youu
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
    # number_photo - это номер фотографии, которую мы хотим получить. Т.к. нельзя отправить сразу несколько фотографий, приходится отправлять по одной
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


class UserSearch(Resource):  # Для поиска пользователей для диалога
    parser = reqparse.RequestParser()
    # Тип диалога, который ищет пользователь может быть search_interests_dialog, search_gender_dialog и stop_dialog
    # Для stop_dialog нужно также указать telegram_id_companion - телеграм айди собеседника
    parser.add_argument('telegram_id', required=True)
    parser.add_argument('type_dialog', required=True)
    parser.add_argument('telegram_id_companion', required=False)

    def post(self):
        # Не зная пароль никто не сможет получить пользователя
        if 'password' not in request.headers:
            abort(400, message='Access error')
        abort_if_password_false(request.headers['password'])

        args = self.parser.parse_args()
        try:
            telegram_id = int(args['telegram_id'])
        except Exception as e:
            return jsonify({'error': 'telegram_id can only contain numbers'})
        abort_if_user_not_found(telegram_id)

        if args['type_dialog'] == 'search_interests_dialog':  # Если мы ищем собеседника по интересам
            start_time = time.time()
            while time.time() - start_time <= 10:
                common_interests_with_now_user = {}  # Словарь совпадений интересов с исходным пользователем
                now_user_interests = set(User.query.filter_by(telegram_id=telegram_id).first().interests)  # Множество интересов исходного пользователя
                search_dialog_users = User.query.filter_by(status_dialog='search_interests_dialog').all()
                for user in search_dialog_users:
                    common_interests_with_now_user[user.telegram_id] = len(now_user_interests & set(user.interests))  # Длина пересечения множеств интересов двух пользователей
                suitable_user = sorted(common_interests_with_now_user.items(), key=lambda x: x[1])[-1]  # Пользователь с наибольшим совпадением интересов
                if User.query.filter_by(telegram_id=telegram_id).first().status_dialog == 'in_dialog':
                    return jsonify({'status': 'user in dialog', 'message': 'User {} is already in dialog'.format(str(telegram_id))})
                if suitable_user[-1] != 0 and User.query.filter_by(
                        telegram_id=suitable_user[0]).first().status_dialog != 'in_dialog':  # Если есть пользователь, с которым совпадает хоть один интерес, и он еще не в диалоге
                    User.query.filter_by(telegram_id=suitable_user[0]).first().status_dialog = 'in_dialog'
                    User.query.filter_by(telegram_id=telegram_id).first().status_dialog = 'in_dialog'
                    db.session.commit()
                    return jsonify({'status': 'OK', 'telegram_id_suitable_user': suitable_user[0]})
            return jsonify({'status': 'not users', 'message': 'The search timed out for 10 seconds. At the moment there are no users with your interests'})
        elif args['type_dialog'] == 'stop_dialog':  # Если нужно прекратить диалог между двумя пользователями
            abort_if_user_not_found(int(args['telegram_id_companion']))
            User.query.filter_by(telegram_id=args['telegram_id_companion']).status_dialog = 'not_in_dialog'
            db.session.commit()
            User.query.filter_by(telegram_id=args['telegram_']).status_dialog = 'not_in_dialog'
            db.session.commit()
            return jsonify({'status': 'OK', 'message': 'User {} and user {} are not in dialog'.format(args['telegram_id_companion'], args['telegram_id'])})


class UserListApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('gender', required=True)
    parser.add_argument('age', required=True)
    parser.add_argument('interests', required=True)
    parser.add_argument('about_me', required=True)
    parser.add_argument('about_you', required=True)
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

        # Проверка информации о собеседнике
        try:
            about_you = str(args['about_you'])
            if len(about_you) > 1000:
                return jsonify({'error': 'maximum about_you length - 1000 symbols'})
        except Exception as e:
            return jsonify(type_error('about_you', str(type(args['about_you']))))
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
api.add_resource(UserSearch, '/api/search_dialog')
