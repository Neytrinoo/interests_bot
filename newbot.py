from telebot import types
import telebot


token = '797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88'

bot = telebot.TeleBot(token)

users = {}

# first_name
# last_name
# age
# sex
# interests
# biography
# about_partner
# photos


@bot.message_handler(commands=['help'])
def help_for_helpless(message):
    bot.send_message(message.from_user.id, "<Полезная инструкция>")


# Сделать кнопку регистрации на начальном экране
@bot.message_handler(commands=['reg'])
def profile_start(message):
    bot.send_message(message.from_user.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, profile_get_name)


@bot.message_handler(content_types=['text'])
def profile_get_name(message):
    if message.text.isalpha() is False:
        bot.send_message(message.from_user.id, 'Текстом, пожалуйста')
        bot.register_next_step_handler(message, profile_get_name)
        return
    users[message.from_user.id] = {}
    users[message.from_user.id]['first_name'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, profile_get_surname)


@bot.message_handler(content_types=['text'])
def profile_get_surname(message):
    if message.text.isalpha() is False:
        bot.send_message(message.from_user.id, 'Текстом, пожалуйста')
        bot.register_next_step_handler(message, profile_get_surname)
        return
    users[message.from_user.id]['last_name'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Сколько вам лет?')
    bot.register_next_step_handler(message, profile_get_age)


@bot.message_handler(content_types=['text'])
def profile_get_age(message):
    try:
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
        bot.send_message(message.from_user.id, 'Ошибка, введите верные данные. Какой у вас пол?')
        bot.register_next_step_handler(message, profile_get_sex)
        return profile_get_sex

    print(users)
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Ваши интересы? (Через запятую)', reply_markup=keyboard_hider)
    bot.register_next_step_handler(message, profile_get_interests)


@bot.message_handler(content_types=['text'])
def profile_get_interests(message):
    users[message.from_user.id]['interests'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Ваша биография?')
    bot.register_next_step_handler(message, profile_get_biography)


@bot.message_handler(content_types=['text'])
def profile_get_biography(message):
    users[message.from_user.id]['biography'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Расскажите о желаемом партнёре?')
    bot.register_next_step_handler(message, profile_get_about_partner)


@bot.message_handler(content_types=['text'])
def profile_get_about_partner(message):
    users[message.from_user.id]['about_partner'] = message.text
    print(users)
    bot.send_message(message.from_user.id, 'Ваши фотографии? (Максимум 4)')
    bot.register_next_step_handler(message, profile_get_photos)


@bot.message_handler(content_types=['photo'])
def profile_get_photos(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_files = bot.download_file(file_info.file_path)

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

        users[message.from_user.id]['photos'] = downloaded_files

        print(users)

    except Exception as e:
        print(e)
        bot.send_message(message.from_user.id, 'Пожалуйста отправьте фото нужного формата')


if __name__ == "__main__":
    bot.polling(none_stop=True)
