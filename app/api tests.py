from requests import get, post, delete, put
from app import db
from app.models import User
# User.query.filter_by(id=3).first().status_dialog = 'not_in_dialog'
import time
# print(get('http://localhost:5000/api/users/1').json())
# f = open('pank.jpg', 'rb').read()
user = {
    'name': 'Геша Горин',
    'gender': 'male',
    'age': '20',
    'interests': 'программирование, Python, философия, биология',
    'about_me': 'Я это я',
    'about_you': 'ты это ты',
    'telegram_id': '23423321',
}
# <Добавление фотографии для пользователя>
# file = {'file': f}
# print(put('http://127.0.0.1:5000/api/users/23423322', headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}, files=file).json())
# <Конец добавления фотографии для пользователя>

# print(put('http://127.0.0.1:5000/api/users/23423323', headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'},
#           json={'interests': 'программирование, Python, философия, биология'}).json())
# print(get('http://127.0.0.1:5000/api/users/23423323', headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}).json())
# print(put('http://127.0.0.1:5000/api/users/425344139', json={'name': 'Не Иван'}).json())
# print(post('http://127.0.0.1:5000/api/users', json=user, headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}).json())
# t = time.time()
# print(get('http://puparass.pythonanywhere.com/api/users/1231', headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}).json())
# print(time.time() - t)

# Получение фотографии пользователя по номеру фотографии
print(get('http://127.0.0.1:5000/api/user_photos/23423322', headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}, json={'number_photo': 1}).content)