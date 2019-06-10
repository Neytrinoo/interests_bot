from app.models import *
from requests import post, get

# user = {
#     'name': 'Не Геннадий Горин',
#     'gender': 'female',
#     'age': '45',
#     'interests': 'философия, биология, программирование, химия',
#     'about_me': 'Я это я',
#     'about_you': 'ты это ты',
#     'telegram_id': '34523421'
# }
# print(post('http://127.0.0.1:5000/api/users', json=user, headers={'password': 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'}).json())

user_interests1 = set(User.query.filter_by(id=1).first().interests)
user_interests2 = set(User.query.filter_by(id=2).first().interests)
intersection = user_interests1 & user_interests2
print(user_interests1, user_interests2)
print(len(intersection))

a = {
    '21312123': 4,
    '12312311': 7,
    '34726382': 3
}
b = sorted(a.items(), key=lambda x: x[1])
print(b[-1][0])
