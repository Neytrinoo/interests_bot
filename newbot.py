from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot


token = '797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88'

bot = telebot.TeleBot(token)

first_name = ""
last_name = ""
age = 0
sex = ""
interests = ""
biography = ""
about_partner = ""
photo = ""


@bot.message_handler(commands=['help'])
def help_for_helpless(message):
    bot.reply_to(message, "<Полезная инструкция>")


# Сделать кнопку регистрации на начальном экране
@bot.message_handler(content_types=['text'])
def profile_start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, profile_get_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg')


@bot.message_handler(content_types=['text'])
def profile_get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, profile_get_surname)


@bot.message_handler(content_types=['text'])
def profile_get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, profile_get_age)


def profile_get_age(message):
    global age
    try:
        age = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, profile_get_age)
        return

    # <buttons>
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton("Мужской", callback_data="male"),
                 InlineKeyboardButton("Женский", callback_data="female"))
    bot.send_message(message.from_user.id, text="Какой у вас пол?", reply_markup=keyboard)
    # </buttons>

    bot.register_next_step_handler(message, profile_get_sex)


# Обработчик для выбора пола
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global sex
    if call.data == "male":
        sex = "male"
    elif call.data == "female":
        sex = "female"


# Переделать под кнопки Муж/Жен
def profile_get_sex(message):
    bot.send_message(message.from_user.id, 'Ваши интересы? (Через запятую)')
    bot.register_next_step_handler(message, profile_get_interests)


@bot.message_handler(content_types=['text'])
def profile_get_interests(message):
    global interests
    interests = message.text
    bot.send_message(message.from_user.id, 'Ваша биография?')
    bot.register_next_step_handler(message, profile_get_biography)


@bot.message_handler(content_types=['text'])
def profile_get_biography(message):
    global biography
    biography = message.text
    bot.send_message(message.from_user.id, 'Расскажите о желаемом партнёре?')
    bot.register_next_step_handler(message, profile_get_about_partner)


@bot.message_handler(content_types=['text'])
def profile_get_about_partner(message):
    global about_partner
    about_partner = message.text
    bot.send_message(message.from_user.id, 'Ваши фотографии? (Максимум 4)')
    bot.register_next_step_handler(message, profile_get_photo)


# Переделать под формат фотографий
# Ещё не знаю работает или нет :D
@bot.message_handler(content_types=['photo'])
def profile_get_photo(message):
    try:
        for mes in message:
            if mes < 4:
                print('good')
            else:
                print('bad')
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)

        bot.reply_to(message, "Данные добавлены")

        # Дим Димыч, используй эту переменную для api
        print(downloaded_file)

        # <test>
        # bot.send_message(message.from_user.id, "Спасибо! Теперь вы можете искать себе партнёра")
        # bot.send_message(message.from_user.id, 'Тебе ' + str(age) + ' лет, тебя зовут ' +
        #                  name + ' ' + surname + '?' + sex)
        # </test>

    except Exception as e:
        print(e)
        bot.send_message(message.from_user.id, 'Не поддерживаемый формат \n Ваши фотографии? (Максимум 4)')
        return


if __name__ == "__main__":
    bot.polling(none_stop=True)
