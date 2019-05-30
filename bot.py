from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
# from telegram import ReplyKeyboardMarkup


def main():
    updater = Updater('797488097:AAFIilpcv61tuQ7kFDtZHZyuPpcE8KuSI88')
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('', ))
    # dp.add_handler(CommandHandler('', ))
    # dp.add_handler(CommandHandler('', ))
    # dp.add_handler(CommandHandler('', ))
    # dp.add_handler(CommandHandler('', ))
    # dp.add_handler(CommandHandler('', ))
    # reply_keyboard = [[''],
    #                   ['']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    # updater.start_polling()
    # updater.idle()


def start_sex(bot, update, user_data):
    update.message.reply_text(
        "Пройди опрос дибил!\n"
        "Это всего лишь данные для фбр, нато, навального и шывцова:\n"
        "Твой пол, ембецил? (Трансгендеры в сделку не входили)"
    )
    return 1


def first_name(bot, update, user_data):
    user_data['sex'] = update.message.text
    update.message.reply_text(
        "Имя?"
    )
    return 2


def last_name(bot, update, user_data):
    user_data['first_name'] = update.message.text
    update.message.reply_text(
        "Фамилия?"
    )
    return 3


def age(bot, update, user_data):
    user_data['last_name'] = update.message.text
    update.message.reply_text(
        "Возраст?"
    )
    return 4


def interests(bot, update, user_data):
    user_data['age'] = update.message.text
    update.message.reply_text(
        "Интересы?"
    )
    return 5


def photo(bot, update, user_data):
    user_data['interests'] = update.message.text
    update.message.reply_text(
        "Фотки?"
    )
    return 6


def biography(bot, update, user_data):
    user_data['photo'] = update.message.text
    update.message.reply_text(
        "Био?"
    )
    return 7


def about_partner(bot, update, user_data):
    user_data['biography'] = update.message.text
    update.message.reply_text(
        "О половом партнере?"
    )
    return 8


def end(bot, update, user_data):
    user_data['about_partner'] = update.message.text
    update.message.reply_text(
        "Сасибо!"
    )
    return ConversationHandler.END


def stop(bot, update):
    update.message.reply_text(
        "Ну и соси!"
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_sex)],

    states={
        1: [MessageHandler(Filters.text, start_sex,
                           pass_user_data=True)],
        2: [MessageHandler(Filters.text, first_name,
                           pass_user_data=True)],
        3: [MessageHandler(Filters.text, last_name,
                           pass_user_data=True)],
        4: [MessageHandler(Filters.text, age,
                           pass_user_data=True)],
        5: [MessageHandler(Filters.text, interests,
                           pass_user_data=True)],
        6: [MessageHandler(Filters.text, photo,
                           pass_user_data=True)],
        7: [MessageHandler(Filters.text, biography,
                           pass_user_data=True)],
        8: [MessageHandler(Filters.text, about_partner,
                           pass_user_data=True)],
        9: [MessageHandler(Filters.text, end,
                           pass_user_data=True)],
    },

    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    main()
