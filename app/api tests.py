from requests import get, post, delete, put

# print(get('http://localhost:5000/api/users/1').json())
user = {
    'name': 'Иванов Иван',
    'gender': 'male',
    'age': '20',
    'interests': 'программирование, Python, философия, биология',
    'about_me': 'Я это я',
    'about_you': 'ты это ты',
    'telegram_id': '23423323'
}
# print(post('http://127.0.0.1:5000/api/users', json=user).json())
# print(put('http://127.0.0.1:5000/api/users/23423323', json={'name': 'Не Иван'}).json())
f = open('pank.jpg')
print(f.read())
