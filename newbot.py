import asyncio
import telebot
from requests import get, post, put
from telebot import types

token = '797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88'
SECRET_PASSWORD = 'yEChQDWrLCXg3zQPvJeEuY25e3EOn0'
SERVER_API_URL = 'http://127.0.0.1:5000/api/users'
SERVER = 'http://127.0.0.1:5000/api'
bot = telebot.TeleBot(token)

users = {}


# Функция проверки, есть ли пользователь в бд или нет. Позже реализую такую функцию на стороне api, пока что мы получаем все данные о пользователе.
# Но эта функция просто будет возвращать боту статус, есть ли пользователь в бд или нет
def is_user_in_db(telegram_id):
    user_in_db = get(SERVER + '/user_exist/' + str(telegram_id), headers={'password': SECRET_PASSWORD})
    if user_in_db.status_code == 200:
        return True
    return False


def render_profile(user):
    profile = 'Никнейм товарища: ' + user['name'] + '\nГендер нашего партийного друга: ' \
              + user['gender'] + '\nКоличество лет, проведенных на заводе: ' + user['age'] \
              + '\nДолжность на заводе: ' + user['about_me'] + '\nЧто этот хрен хочет от тебя: ' \
              + user['about_you'] + '\nЧто в голове у этого буржуя, кроме завода: ' \
              + user['interests']
    return profile


# Получение одной фотографии пользователя по номеру фотографии
async def get_user_photo(telegram_id, number_photo):
    with get(SERVER + '/user_photos/' + str(telegram_id), headers={'password': SECRET_PASSWORD}, json={'number_photo': str(number_photo)}) as response:
        users[telegram_id]['photos'].append(response.content)


# Асинхронное получение фотографии пользователя по его телеграм айди. Нужно указать количество фотографий.
# Чтобы это кол-во получить, нужно получить пользователя из бд и взять из ответа поле count_photos
# Полученные с сервера фотографии будут храниться в словаре users[telegram_id]['photos'] в массиве
async def get_user_photos(telegram_id, count_photos):
    tasks = []
    users[telegram_id]['photos'] = []
    for i in range(count_photos):
        task = asyncio.create_task(get_user_photo(telegram_id, i))
        tasks.append(task)
    await asyncio.gather(*tasks)


# Редактирование полей пользовательской анкеты. field_name - название поля, которое надо отредактировать, field_value - значение для изменения поля
def edit_profile(telegram_id, field_name, field_value):
    res = put(SERVER + '/users/' + str(telegram_id), headers={'password': SECRET_PASSWORD}, json={field_name: field_value}).json()
    return res


# Функция для получения всех полей пользовательской анкеты из бд
def get_user_from_db(telegram_id):
    user_in_db = get(SERVER_API_URL + '/' + str(telegram_id), headers={'password': SECRET_PASSWORD}).json()['user']
    return user_in_db


def get_companion_telegram_id(telegram_id, type_dialog):
    telegram_id_friend = post(SERVER + '/search_dialog', headers={'password': SECRET_PASSWORD},
                              json={'telegram_id': str(telegram_id), 'type_dialog': type_dialog})
    return telegram_id_friend


# Функция прерывания диалога между двумя пользователями
def stop_dialog(telegram_id1, telegram_id2):
    stop = post(SERVER + '/search_dialog', headers={'password': SECRET_PASSWORD},
                json={'telegram_id': str(telegram_id1), 'telegram_id_companion': str(telegram_id2), 'type_dialog': 'stop_dialog'})
    return stop.json()


# 4 ПУНКТ ЗАДАНИЯ
@bot.message_handler(commands=['show_profile'])
def show_profile(message):
    if is_user_in_db(message.from_user.id):
        user_in_db = get_user_from_db(message.from_user.id)  # Зачем ты каждый раз преобразовывал к джейсону, если можно сделать это сразу, оло
        print(user_in_db)
        profile = 'Имя: ' + user_in_db['name'] + '\nПол: ' \
                  + user_in_db['gender'] + '\nКоличество прожитых годикофф: ' + user_in_db['age'] \
                  + '\nО вас: ' + user_in_db['about_me'] + '\nО желаемом собеседнике: ' \
                  + user_in_db['about_you'] + '\nВаши интересы: ' \
                  + user_in_db['interests']
        bot.send_message(message.from_user.id, profile)
    else:
        bot.send_message(message.from_user.id, 'Для начала добавьте анкету - /reg')


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
@bot.message_handler(commands=['search_interests'], content_types=["text", "sticker", "pinned_message", "photo", "audio"])
def search_interests(message):
    if not is_user_in_db(message.from_user.id):
        bot.send_message(message.from_user.id, 'Сначала вам нужно добавить анкету. Для этого напишите /reg')
        return
    user_in_db = get_user_from_db(message.from_user.id)

    if message.from_user.id in users and 'dialog' in users[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Вы уже в диалоге, оло')
    telegram_id_friend = get_companion_telegram_id(user_in_db['telegram_id'], 'search_interests_dialog').json()
    print(telegram_id_friend)
    if 'status' in telegram_id_friend and telegram_id_friend['status'] == 'OK':
        mes = 'Собеседник в абсолютности своей найден. Теперь вы можете общаться. Ах, да, вот его анкета\n\n'
        users[message.from_user.id] = {}
        users[message.from_user.id]['dialog'] = telegram_id_friend['telegram_id_suitable_user']
        users[telegram_id_friend['telegram_id_suitable_user']] = {}
        users[telegram_id_friend['telegram_id_suitable_user']]['dialog'] = message.from_user.id
        bot.send_message(int(telegram_id_friend['telegram_id_suitable_user']), mes + render_profile(user_in_db))
        companion_profile = get_user_from_db(telegram_id_friend['telegram_id_suitable_user'])

        bot.send_chat_action(message.from_user.id, render_profile(companion_profile))

    elif telegram_id_friend['status'] == 'user in dialog':  # Если пользователь уже в диалоге(такое может быть, и сервер за этим следит), то ничего не делаем.
        # Пользователь получит сообщение о том, что он в диалоге от другого пользователя
        pass
    else:
        bot.send_message(message.from_user.id, 'Увы, но почему-то собеседников с подходящими для вас интересами не обнаружилось. '
                                               'Попробуйте поискать позже, изменить интересы или выполнить поиск по полу (/search_male /search_female)')
    return


# Редактирование профиля
@bot.message_handler(commands=['edit_profile'])
def edit_prof(message):
    if message.from_user.id in users and 'dialog' in users[message.from_user.id]:
        bot.send_message(message.from_user.id, "БИСТРА ВИШЕЛ С ДИЛОГА!")
    if message.from_user.id in users:
        markup = types.ReplyKeyboardMarkup()
        item_button1 = types.KeyboardButton('Никнейм')
        item_button2 = types.KeyboardButton('Пол')
        item_button3 = types.KeyboardButton('Возраст')
        item_button4 = types.KeyboardButton('О вас')
        item_button5 = types.KeyboardButton('О собеседнике')
        item_button6 = types.KeyboardButton('Интересы')
        item_button7 = types.KeyboardButton('Фото')
        item_button8 = types.KeyboardButton('Прекратить редактировние')
        markup.row(item_button1, item_button2, item_button3)
        markup.row(item_button4, item_button5, item_button6)
        markup.row(item_button7, item_button8)
        # markup = types.ForceReply(selective=False)
        bot.send_message(message.from_user.id, "Что вы хотите изменить:", reply_markup=markup)
        bot.register_next_step_handler(message, check_answer)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):

    keyboard_hider = types.ReplyKeyboardRemove()

    if message.text == 'Никнейм':
        bot.send_message(message.from_user.id, "Новый желаемый никнейм:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_name)
    elif message.text == 'Пол':
        bot.send_message(message.from_user.id, "Новый желаемый пол:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_gender)
    elif message.text == 'Возраст':
        bot.send_message(message.from_user.id, "Новый желаемый возраст:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_age)
    elif message.text == 'О вас':
        bot.send_message(message.from_user.id, "Изменение биографии:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_about_me)
    elif message.text == 'О собеседнике':
        bot.send_message(message.from_user.id, "Изменение желаний о собеседнике:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_about_you)
    elif message.text == 'Интересы':
        bot.send_message(message.from_user.id, "Новые интересы:", reply_markup=keyboard_hider)
        bot.register_next_step_handler(message, check_answer_interests)
    elif message.text == 'Фото':
        keyboard = types.ReplyKeyboardMarkup(row_width=2)
        keyboard.add(types.KeyboardButton('/skip_photos'), types.KeyboardButton('/stop_photos'))
        bot.send_message(message.from_user.id,
                         'Ваши фотографии? (Максимум 4). Если вы не хотите добавлять фотографии, напишите /skip_photos \n Если вы добавили нужные вам фотографии,'
                         'напишите /stop_photos', reply_markup=keyboard)
        bot.register_next_step_handler(message, profile_get_photos)
    elif message.text == 'Прекратить редактировние':
        bot.send_message(message.from_user.id, "Oh shit here we go again", reply_markup=keyboard_hider)
        # HELP: Куда эта запупа должна вести?
        # bot.register_next_step_handler(message, XZ_link(Главная менюшка))
    else:
        bot.send_message(message.from_user.id, 'Так дело не пойдет')
        return
    return


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_name(message):
    if len(message.text) >= 50:
        bot.send_message(message.from_user.id, 'Введите ваше настоящее имя')
        bot.register_next_step_handler(message, check_answer_name)
        return
    edit_profile(message.from_user.id, 'name', message.text)
    bot.register_next_step_handler(message, edit_prof)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_gender(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton('Мужской'), types.KeyboardButton('Женский'))
    bot.send_message(message.from_user.id, "Какой у вас пол?", reply_markup=keyboard)
    types.ReplyKeyboardRemove(selective=False)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_gender_2(message):
    btn_sex = message.text.lower()
    if btn_sex == "мужской":
        active_sex = "male"
        edit_profile(message.from_user.id, 'gender', active_sex)
        types.ReplyKeyboardRemove(selective=True)
        bot.register_next_step_handler(message, edit_prof)
    elif btn_sex == "женский":
        active_sex = "female"
        edit_profile(message.from_user.id, 'gender', active_sex)
        types.ReplyKeyboardRemove(selective=True)
        bot.register_next_step_handler(message, edit_prof)
    else:
        bot.send_message(message.from_user.id, 'Введите верные данные. Какой у вас пол?')
        bot.register_next_step_handler(message, check_answer_gender_2)
        return check_answer_gender_2


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_age(message):
    try:
        if int(message.text) >= 70 or int(message.text) <= 10:
            bot.send_message(message.from_user.id, 'Введите ваш настоящий возраст')
            bot.register_next_step_handler(message, check_answer_age)
            return
        edit_profile(message.from_user.id, 'age', message.text)
        bot.register_next_step_handler(message, edit_prof)
    except ValueError:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, check_answer_age)
        return


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_about_me(message):
    if len(message.text) >= 1000:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 1000 символов')
        bot.register_next_step_handler(message, check_answer_about_me)
        return check_answer_about_me
    edit_profile(message.from_user.id, 'about_me', message.text)
    bot.register_next_step_handler(message, edit_prof)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_about_you(message):
    if len(message.text) >= 1000:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 1000 символов')
        bot.register_next_step_handler(message, check_answer_about_you)
        return check_answer_about_you
    edit_profile(message.from_user.id, 'about_you', message.text)
    bot.register_next_step_handler(message, edit_prof)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer_interests(message):
    p_interests = message.text.split(',')
    for i in range(len(p_interests)):
        p_interests[i] = p_interests[i].lower().lstrip().rstrip()
        if len(p_interests[i]) >= 256:
            bot.send_message(message.from_user.id, 'Длина одного из интересов не может превышать 256 символов')
            bot.register_next_step_handler(message, check_answer_interests)
            return check_answer_interests
    edit_profile(message.from_user.id, 'interests', message.text)
    bot.register_next_step_handler(message, edit_prof)


# @bot.message_handler(content_types=['photo', 'text'])
# def check_answer_photos(message):
#     keyboard_hider = types.ReplyKeyboardRemove()
#     try:
#         file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
#         downloaded_file = bot.download_file(file_info.file_path)
#         if len(users[message.from_user.id]['photos']) <= 3:
#             edit_profile(message.from_user.id, 'photos', message.photo.append(downloaded_file))
#             # users[message.from_user.id]['photos'].append(downloaded_file)
#             if len(users[message.from_user.id]['photos']) > 3:
#                 bot.send_message(message.from_user.id, 'Вы успешно добавили 4 фотографии. Ваша анкета изменена, ура!', reply_markup=keyboard_hider)
#                 # register_user(users[message.from_user.id])
#                 edit_profile(message.from_user.id, 'interests', message.photo)
#                 return
#             bot.send_message(message.from_user.id, 'Фото номер ' + str(len(users[message.from_user.id]['photos'])) + ' добавлено')
#         else:
#             bot.send_message(message.from_user.id, '4 первые фотографии были добавлены, но больше вы добавить не можете.')
#         print(len(users[message.from_user.id]['photos']))
#
#     except Exception as e:
#         btn_photo = message.text.lower()
#         print(btn_photo)
#         if btn_photo == '/skip_photos':
#             bot.send_message(message.from_user.id, 'Вы ещё можете добавить фотографии в любой момент',
#                              reply_markup=keyboard_hider)
#             register_user(users[message.from_user.id])
#             return
#             # bot.register_next_step_handler(message, следующая функция)
#         elif btn_photo == '/stop_photos':
#             if len(users[message.from_user.id]['photos']) >= 1:
#                 bot.send_message(message.from_user.id, 'Вы ещё можете пополнить фотографии вашего профиля в любой момент',
#                                  reply_markup=keyboard_hider)
#                 register_user(users[message.from_user.id])
#                 return
#                 # bot.register_next_step_handler(message, следующая функция)
#             else:
#                 bot.send_message(message.from_user.id,
#                                  'Для остановки подачи фотографий вам нужно иметь хотя бы больше одной фотографии')
#                 bot.register_next_step_handler(message, profile_get_photos)
#                 return profile_get_photos
#         else:
#             print(e)
#             bot.send_message(message.from_user.id, 'Пожалуйста отправьте фото нужного формата')
#             bot.register_next_step_handler(message, profile_get_photos)
#             return profile_get_photos


# Остановка диалога
@bot.message_handler(commands=['stop_dialog'])
def stop_dial(message):
    if message.from_user.id in users and 'dialog' in users[message.from_user.id]:
        stop_dialog(message.from_user.id, users[message.from_user.id]['dialog'])
        bot.send_message(message.from_user.id, 'Диалог остановлен. Чтобы начать поиск заново, напишите /search_interests')
        bot.send_message(users[message.from_user.id]['dialog'], 'Диалог остановлен. Чтобы начать поиск заново, напишите /search_interests')
        print(users)
        del users[users[message.from_user.id]['dialog']]
        del users[message.from_user.id]
    else:
        bot.send_message(message.from_user.id, "Доцл, что бы остановить диалог нужно быть в нём!")
        return
    return


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
# 1 ПУНКТ ЗАДАНИЯ
def profile_pre_start(message):
    if is_user_in_db(message.from_user.id) is True:
        if message.from_user.id in users and 'dialog' in users[message.from_user.id]:
            id_friend = users[message.from_user.id]['dialog']
            bot.send_message(id_friend, message.text)
        else:
            bot.send_message(message.from_user.id, 'Вам нужно написать /search_interests чтобы найти собеседника со схожими с вашими интересами')
    else:
        bot.send_message(message.from_user.id, 'Сначала нужно зарегистрировать анкету (/reg - для регистрации)')


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


@bot.message_handler(content_types=['photo', 'text'])
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
        print(btn_photo)
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


if __name__ == "__main__":
    bot.polling(none_stop=True)
