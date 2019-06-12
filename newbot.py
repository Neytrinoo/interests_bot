import asyncio
import telebot
from requests import get, post, put
from telebot import types

token = '797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88'
SECRET_PASSWORD = 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'
SERVER_API_URL = 'http://puparass.pythonanywhere.com/api/users'
bot = telebot.TeleBot(token)

users = {}


# Функция проверки, есть ли пользователь в бд или нет. Позже реализую такую функцию на стороне api, пока что мы получаем все данные о пользователе.
# Но эта функция просто будет возвращать боту статус, есть ли пользователь в бд или нет
def is_user_in_db(telegram_id):
    user_in_db = get(SERVER_API_URL + '/' + str(telegram_id), headers={'password': SECRET_PASSWORD})
    if user_in_db.status_code == 200:
        return True
    return False


# Функция для получения всех полей пользовательской анкеты из бд
def get_user_from_db(telegram_id):
    user_in_db = get(SERVER_API_URL + '/' + str(telegram_id), headers={'password': SECRET_PASSWORD})
    return user_in_db


def get_companion_telegram_id(telegram_id, type_dialog):
    telegram_id_friend = post('http://puparass.pythonanywhere.com/api/search_dialog', headers={'password': SECRET_PASSWORD},
                              json={'telegram_id': str(telegram_id), 'type_dialog': type_dialog})
    return telegram_id_friend


@bot.message_handler(commands=['help'])
def help_for_helpless(message):
    bot.send_message(message.from_user.id, "<Полезная инструкция>")


# Сделать кнопку регистрации на начальном экране
@bot.message_handler(commands=['reg'])
def profile_start(message):
    if message.from_user.id in users:
        bot.send_message(message.from_user.id, 'Вам недоступна эта команда')
        return
    if is_user_in_db(message.from_user.id):
        bot.send_message(message.from_user.id, 'Ваша анкета была добавлена ранее. Вы можете отредактировать ее')
        return
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "Как вас зовут?", reply_markup=keyboard_hider)
    bot.register_next_step_handler(message, profile_get_name)


# Команда поиска собеседника по интересам
@bot.message_handler(commands=['search_interests'])
def search_interests(message):
    user_in_db = get_user_from_db(message.from_user.id)
    if not is_user_in_db(message.from_user.id):
        bot.send_message(message.from_user.id, 'Сначала вам нужно добавить анкету. Для этого напишите /reg')
        return
    if 'dialog' in users[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Вы уже в диалоге, оло')
    telegram_id_friend = get_companion_telegram_id(user_in_db.json()['telegram_id'], 'search_interests_dialog').json()
    if 'status' in telegram_id_friend and telegram_id_friend['status'] == 'OK':
        mes = 'Собеседник в абсолютности своей найден. Теперь вы можете общаться. Ах, да, вот его анкета\n'
        users[message.from_user.id]['dialog'] = telegram_id_friend['telegram_id_suitable_user']
        users[telegram_id_friend['telegram_id_suitable_user']]['dialog'] = message.from_user.id
        bot.send_message(message.from_user.id, mes + str(get_user_from_db(telegram_id_friend['telegram_id_suitable_user']).json()))
        bot.send_message(int(telegram_id_friend['telegram_id_suitable_user']), mes + str(user_in_db.json()))
    elif telegram_id_friend['status'] == 'user in dialog':  # Если пользователь уже в диалоге(такое может быть, и сервер за этим следит), то ничего не делаем.
        # Пользователь получит сообщение о том, что он в диалоге от другого пользователя
        pass
    else:
        bot.send_message(message.from_user.id, 'Увы, но почему-то собеседников с подходящими для вас интересами не обнаружилось. '
                                               'Попробуйте поискать позже, изменить интересы или выполнить поиск по полу (/search_male /search_female)')
    return


@bot.message_handler(content_types=['text'])
def profile_pre_start(message):
    if 'dialog' in users[message.from_user.id]:
        id_friend = users[message.from_user.id]['dialog']
        bot.send_message(id_friend, message.text)


# Скип добавления фотографий, если пользователь не хочет их добавлять
@bot.message_handler(commands=['skip_photos'])
def profile_skip_photos(message):
    if message.from_user.id not in users:
        bot.send_message(message.from_user.id, 'Вам недоступна эта команда')
        return
    if 'photos' not in users[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Вы еще не дошли до добавления фотографий')
        return
    users[message.from_user.id]['photos'] = []
    register_user(users[message.from_user.id])
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Ваша анкета успешно добавлена, уря!', reply_markup=keyboard_hider)
    print(users)


# Остановка добавления фотографий, если пользователь добавил все, что хотел
@bot.message_handler(commands=['stop_photos'])
def profile_stop_photos(message):
    if message.from_user.id not in users:
        bot.send_message(message.from_user.id, 'Вам недоступна эта команда')
        return
    if 'photos' not in users[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Вы еще не дошли до добавления фотографий')
        return
    if not users[message.from_user.id]['photos']:
        bot.send_message(message.from_user.id, 'Вы еще не добавили ни одной фотографии')
        return
    register_user(users[message.from_user.id])
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Ваша анкета успешно добавлена, ура!', reply_markup=keyboard_hider)


@bot.message_handler(content_types=['text'])
def profile_pre_start(message):
    bot.send_message(message.from_user.id, "Введите комманду /reg для регистрации")


@bot.message_handler(content_types=['text'])
def profile_get_name(message):
    if len(message.text) >= 50:
        bot.send_message(message.from_user.id, 'Введите ваше настоящее имя')
        bot.register_next_step_handler(message, profile_get_name)
        return
    users[message.from_user.id] = {}
    users[message.from_user.id]['telegram_id'] = message.from_user.id
    users[message.from_user.id]['name'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Сколько вам лет?')
    bot.register_next_step_handler(message, profile_get_age)


@bot.message_handler(content_types=['text'])
def profile_get_age(message):
    try:
        if int(message.text) >= 70 or int(message.text) <= 10:
            bot.send_message(message.from_user.id, 'Введите ваш настоящий возраст')
            bot.register_next_step_handler(message, profile_get_age)
            return
        users[message.from_user.id]['age'] = int(message.text)
        users[message.from_user.id]['age'] = message.text
        print(users)
    except ValueError:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, profile_get_age)
        return

    # <buttons>
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton('Мужской'), types.KeyboardButton('Женский'))
    bot.send_message(message.from_user.id, "Какой у вас пол?", reply_markup=keyboard)
    types.ReplyKeyboardRemove(selective=False)
    # </buttons>

    bot.register_next_step_handler(message, profile_get_sex)


# Имеется встроенный обработчик для выбора пола
@bot.message_handler(func=lambda message: True, content_types=['text'])
def profile_get_sex(message):
    btn_sex = message.text.lower()
    if btn_sex == "мужской":
        active_sex = "male"
        users[message.from_user.id]['gender'] = active_sex
    elif btn_sex == "женский":
        active_sex = "female"
        users[message.from_user.id]['gender'] = active_sex
    else:
        bot.send_message(message.from_user.id, 'Введите верные данные. Какой у вас пол?')
        bot.register_next_step_handler(message, profile_get_sex)
        return profile_get_sex

    print(users)
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Ваши интересы? (Через запятую)', reply_markup=keyboard_hider)
    bot.register_next_step_handler(message, profile_get_interests)


@bot.message_handler(content_types=['text'])
def profile_get_interests(message):
    p_interests = message.text.split(',')
    for i in range(len(p_interests)):
        p_interests[i] = p_interests[i].lower().lstrip().rstrip()
        if len(p_interests[i]) >= 256:
            bot.send_message(message.from_user.id, 'Длина одного из интересов не может превышать 256 символов')
            bot.register_next_step_handler(message, profile_get_interests)
            return profile_get_interests
    users[message.from_user.id]['interests'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Ваша биография?')
    bot.register_next_step_handler(message, profile_get_biography)


@bot.message_handler(content_types=['text'])
def profile_get_biography(message):
    if len(message.text) >= 1000:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 1000 символов')
        bot.register_next_step_handler(message, profile_get_biography)
        return profile_get_biography
    users[message.from_user.id]['about_me'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Расскажите о желаемом партнёре?')
    bot.register_next_step_handler(message, profile_get_about_partner)


@bot.message_handler(content_types=['text'])
def profile_get_about_partner(message):
    if len(message.text) >= 1000:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 1000 символов')
        bot.register_next_step_handler(message, profile_get_about_partner)
        return profile_get_about_partner
    users[message.from_user.id]['about_you'] = message.text
    print(users)
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton('/skip_photos'), types.KeyboardButton('/stop_photos'))
    bot.send_message(message.from_user.id, 'Ваши фотографии? (Максимум 4). Если вы не хотите добавлять фотографии, напишите /skip_photos \n Если вы добавили нужные вам фотографии,'
                                           'напишите /stop_photos', reply_markup=keyboard)
    bot.register_next_step_handler(message, profile_get_photos)
    users[message.from_user.id]['photos'] = []


@bot.message_handler(content_types=['photo'])
def profile_get_photos(message):
    keyboard_hider = types.ReplyKeyboardRemove()
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if len(users[message.from_user.id]['photos']) <= 3:
            users[message.from_user.id]['photos'].append(downloaded_file)
            if len(users[message.from_user.id]['photos']) > 3:
                bot.send_message(message.from_user.id, 'Вы успешно добавили 4 фотографии. Ваша анкета зарегистрирована, ура!', reply_markup=keyboard_hider)
                register_user(users[message.from_user.id])
                return
            bot.send_message(message.from_user.id, 'Фото номер ' + str(len(users[message.from_user.id]['photos'])) + ' добавлено')
        else:
            bot.send_message(message.from_user.id, '4 первые фотографии были добавлены, но больше вы добавить не можете.')
        print(len(users[message.from_user.id]['photos']))

    except Exception as e:
        btn_photo = message.text.lower()
        if btn_photo == '/skip_photos':
            bot.send_message(message.from_user.id, 'Вы ещё можете добавить фотографии в любой момент',
                             reply_markup=keyboard_hider)
            register_user(users[message.from_user.id])
            return
            # bot.register_next_step_handler(message, следующая функция)
        elif btn_photo == '/stop_photos':
            if len(users[message.from_user.id]['photos']) >= 1:
                bot.send_message(message.from_user.id, 'Вы ещё можете пополнить фотографии вашего профиля в любой момент',
                                 reply_markup=keyboard_hider)
                register_user(users[message.from_user.id])
                return
                # bot.register_next_step_handler(message, следующая функция)
            else:
                bot.send_message(message.from_user.id,
                                 'Для остановки подачи фотографий вам нужно иметь хотя бы больше одной фотографии')
                bot.register_next_step_handler(message, profile_get_photos)
                return profile_get_photos
        else:
            print(e)
            bot.send_message(message.from_user.id, 'Пожалуйста отправьте фото нужного формата')
            bot.register_next_step_handler(message, profile_get_photos)
            return profile_get_photos


# Добавление фотографии для пользовательской анкеты
async def add_photo(telegram_id, photo):
    img = {'file': photo}
    with put(SERVER_API_URL + '/' + str(telegram_id), headers={'password': SECRET_PASSWORD}, files=img) as response:
        res = response.json()
        print(res)


# Создание асинхронных тасков для добавление фотографий
async def add_user_photos(telegram_id, photos):
    tasks = []
    for photo in photos:
        task = asyncio.create_task(add_photo(telegram_id, photo))
        tasks.append(task)
    await asyncio.gather(*tasks)


# Добавление анкеты пользователя и запуск добавления фотографий, если они есть
def register_user(user):
    new_user = {}
    for key, value in user.items():
        if key != 'photos':
            new_user[key] = value
    print('Добавление пользователя:', post(SERVER_API_URL, headers={'password': SECRET_PASSWORD}, json=new_user).json())
    if user['photos']:  # Если у пользователя есть фотографии, то добавляем их
        asyncio.run(add_user_photos(user['telegram_id'], user['photos']))


# def search_brother(message):
#     users[message.from_user.id]['dialog']


if __name__ == "__main__":
    bot.polling(none_stop=True)
