from telebot import types
import telebot


token = '797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88'

bot = telebot.TeleBot(token)

users = {}

# name
# age
# sex
# interests
# biography
# about_partner
# photos
# telegram_id


@bot.message_handler(commands=['help'])
def help_for_helpless(message):
    bot.send_message(message.from_user.id, "<Полезная инструкция>")


# Сделать кнопку регистрации на начальном экране
@bot.message_handler(commands=['reg'])
def profile_start(message):
    bot.send_message(message.from_user.id, "Как вас зовут?")
    bot.register_next_step_handler(message, profile_get_name)


@bot.message_handler(content_types=['text'])
def profile_get_name(message):
    if message.text.isalpha() is False:
        bot.send_message(message.from_user.id, 'Текстом, пожалуйста')
        bot.register_next_step_handler(message, profile_get_name)
        return
    if len(message.text) >= 50:
        bot.send_message(message.from_user.id, 'Введите ваше настоящее имя')
        bot.register_next_step_handler(message, profile_get_name)
        return
    users[message.from_user.id] = {}
    users[message.from_user.id]['telegram_id'] = message.from_user.id
    users[message.from_user.id]['first_name'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Сколько вам лет?')
    bot.register_next_step_handler(message, profile_get_age)


# @bot.message_handler(content_types=['text'])
# def profile_get_surname(message):
#     if message.text.isalpha() is False:
#         bot.send_message(message.from_user.id, 'Текстом, пожалуйста')
#         bot.register_next_step_handler(message, profile_get_surname)
#         return
#     if len(message.text) >= 200:
#         bot.send_message(message.from_user.id, 'Введите вашу настоящую фамилию')
#         bot.register_next_step_handler(message, profile_get_surname)
#         return
#     users[message.from_user.id]['last_name'] = message.text
#     print(users)
#     bot.send_message(message.from_user.id, 'Сколько вам лет?')
#     bot.register_next_step_handler(message, profile_get_age)


@bot.message_handler(content_types=['text'])
def profile_get_age(message):
    try:
        if int(message.text) >= 70 or int(message.text) <= 10:
            bot.send_message(message.from_user.id, 'Введите ваш настоящий возраст')
            bot.register_next_step_handler(message, profile_get_age)
            return
        users[message.from_user.id]['age'] = int(message.text)
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


# Старый обработчик для выбора пола
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def callback_worker(message):
#     btn_sex = message.text
#     if btn_sex == "Мужской":
#         active_sex = "Мужской"
#         users[message.from_user.id]['sex'] = active_sex
#     elif btn_sex == "Женский":
#         active_sex = "female"
#         users[message.from_user.id]['sex'] = active_sex
#     else:
#         bot.send_message(message.from_user.id, 'Ошибка, введите верные данные')
#         bot.register_next_step_handler(message, callback_worker)
#         return callback_worker
#
#     print(users)
#     bot.register_next_step_handler(message, profile_get_sex)


# Имеется встроенный обработчик для выбора пола
@bot.message_handler(func=lambda message: True, content_types=['text'])
def profile_get_sex(message):
    btn_sex = message.text
    if btn_sex == "Мужской":
        active_sex = "Мужской"
        users[message.from_user.id]['sex'] = active_sex
    elif btn_sex == "Женский":
        active_sex = "Женский"
        users[message.from_user.id]['sex'] = active_sex
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
        if len(p_interests[i]) >= 128:
            bot.send_message(message.from_user.id, 'Длина одного из интересов не может превышать 256 символов')
            bot.register_next_step_handler(message, profile_get_interests)
            return profile_get_interests
    users[message.from_user.id]['interests'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Ваша биография?')
    bot.register_next_step_handler(message, profile_get_biography)


@bot.message_handler(content_types=['text'])
def profile_get_biography(message):
    if len(message.text) >= 256:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 256 символов')
        bot.register_next_step_handler(message, profile_get_biography)
        return profile_get_biography
    users[message.from_user.id]['biography'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Расскажите о желаемом партнёре?')
    bot.register_next_step_handler(message, profile_get_about_partner)


@bot.message_handler(content_types=['text'])
def profile_get_about_partner(message):
    if len(message.text) >= 1000:
        bot.send_message(message.from_user.id, 'Длина биографии не может превышать 1000 символов')
        bot.register_next_step_handler(message, profile_get_about_partner)
        return profile_get_about_partner
    users[message.from_user.id]['about_partner'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Ваши фотографии? (Максимум 4)')
    bot.register_next_step_handler(message, profile_get_photos)


@bot.message_handler(content_types=['photo'])
def profile_get_photos(message):
    try:
        # file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        # downloaded_file = bot.download_file(file_info.file_path)

        # for photo in message.photo:

        # for m in message:
        #     file_info = bot.get_file(m.photo[len(m.photo) - 1].file_id)
        #     downloaded_file = bot.download_file(file_info.file_path)
        #     users[message.from_user.id]['photo'] = downloaded_file
        #     print('Отправка в БД')
        #     bot.reply_to(message, "Фото добавлено")
        #     del users[message.from_user.id]['photo']

        # # Добавление фотографии в словарь
        # users[message.from_user.id]['photo'] = downloaded_files
        #
        # # Отправлка в БД
        # print('Отправлка в БД')

        # for photo in file_info.file_path:
        #     users[message.from_user.id]['photo'] = downloaded_file
        #     print('Отправлка в БД')
        #     bot.reply_to(message, "Фото добавлено")
        #     del users[message.from_user.id]['photo']

        #     # users[message.from_user.id]['photo'] = [downloaded_files]
        #     # print(users)
        #
        #     # for file in downloaded_files:
        #     #     files = [].append(file)
        #
        #     files = [file for file in downloaded_files]
        #
        #     users[message.from_user.id]['photos'] = files
        #
        #     f = open('text.txt', 'w')
        #
        #     f.write(str(downloaded_files))
        #
        #     f.close()

        print(users)

    except Exception as e:
        print(e)
        bot.send_message(message.from_user.id, 'Пожалуйста отправьте фото нужного формата')
        bot.register_next_step_handler(message, profile_get_photos)
        return profile_get_photos


if __name__ == "__main__":
    bot.polling(none_stop=True)
