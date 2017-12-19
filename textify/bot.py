# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup

from utils import find_and_crop, get_cropped_images, shrink_originals, get_scanned_images, user_has_cropped_images, \
    user_has_scanned_images, shrink_cropped

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging

from utils import load_and_save_image,\
    delete_images_for_user, user_has_images,\
    get_originals_pdf, get_cropped_pdf,\
    get_scanned_pdf


from settings import BOTTOKEN

DOCUMENT_TIMEOUT = 80
NO_IMAGES_MSG = "You have to send me an image as file (document) first!"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""
    Hi there! 
Look what i can:
    - scan (shrink) images /scan
    - find documents on images and crop them /find (BETA: unstable)
    - create pdfs /pdf
    
To start just send me an image as file (document).
    """)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("""


Then you'll have a few options:
    - find the document on photo - /find (BETA: unstable)
    - "scan" and reduce size /scan
    - load a series of images "scan" and reduce their size and get _pdf_
    """, parse_mode="Markdown")


def text_handler(bot, update):
    """Echo the user message."""
    text = update.message.text
    reply_markup = ReplyKeyboardRemove()
    update.message.reply_text(text, reply_markup=reply_markup)


def image(bot, update):
    """Instruct that image should be send as file."""
    update.message.reply_text("Image should be send as a file (document)!")


"""
- type /finish to remove images from our server (they are deleted automatically every 30 minutes)
"""


def handle_file(bot, update):
    document = update.message.document
    mime_type = document['mime_type']
    chat_id = update.effective_chat['id']
    if mime_type.split('/')[0] == 'image':

        file = bot.get_file(document['file_id'])
        saved = load_and_save_image(chat_id=chat_id, url=file.file_path)
        if saved:
            custom_keyboard = [['/scan', '/find'], ['/find_and_scan'], ['/pdf']]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
            update.message.reply_text('Got your image!\nSend more images or choose one of options bellow: ',
                                      reply_markup=reply_markup)
    else:
        update.message.reply_text("Bro, pls send me a legit image (as a file)!")


def delete_handler(bot, update):
    chat_id = update.effective_chat['id']
    deleted = delete_images_for_user(chat_id)
    reply_markup = ReplyKeyboardRemove()
    if deleted:
        update.message.reply_text("Your images are gone from my server!", reply_markup=reply_markup)
    else:
        update.message.reply_text("I don't have any of your images!", reply_markup=reply_markup)


def find_handler(bot, update):
    chat_id = update.effective_chat['id']
    if user_has_images(chat_id):
        found_all = find_and_crop(chat_id)
        cropped = get_cropped_images(chat_id)
        if not found_all:
            msg = "I wasn't able to find document on some images =("
        else:
            msg = "I found something on every image!"

        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text(msg, reply_markup=reply_markup)

        for img in cropped:
            bot.send_document(chat_id=update.message.chat_id, document=open('%s' % str(img), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Get cropped PDF", callback_data='cropped_pdf'),
                     InlineKeyboardButton("Get originals PDF", callback_data='originals_pdf')],
                    [InlineKeyboardButton("Scan cropped images", callback_data='scan_cropped')],
                    [InlineKeyboardButton("Delete images", callback_data='delete')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Images processed! Choose one option:", reply_markup=reply_markup)

    else:
        update.message.reply_text(NO_IMAGES_MSG)


def scan_handler(bot, update):
    chat_id = update.effective_chat['id']
    if user_has_images(chat_id):
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text("Started scanning (it may take up too 30 seconds per image)!",
                                  reply_markup=reply_markup)

        shrink_originals(chat_id)
        scanned = get_scanned_images(chat_id)

        for img in scanned:
            bot.send_document(chat_id=update.message.chat_id, document=open('%s' % str(img), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Get scanned PDF", callback_data='scanned_pdf')],
                    [InlineKeyboardButton("Get originals PDF", callback_data='originals_pdf')],
                    [InlineKeyboardButton("Delete images", callback_data='delete')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Images processed! Choose one option:", reply_markup=reply_markup)
    else:
        update.message.reply_text(NO_IMAGES_MSG)


def find_and_scan_handler(bot, update):
    chat_id = update.effective_chat['id']
    if user_has_images(chat_id):
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text("Started cropping!", reply_markup=reply_markup)
        found_all = find_and_crop(chat_id)

        if not found_all:
            msg = "I wasn't able to find document on some images =("
        else:
            msg = "I found something on every image!"

        update.message.reply_text(msg)

        update.message.reply_text("Started scanning (it may take up too 30 seconds per image)!")
        shrink_cropped(chat_id)
        scanned = get_scanned_images(chat_id)

        for img in scanned:
            bot.send_document(chat_id=update.message.chat_id, document=open('%s' % str(img), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Get final PDF", callback_data='scanned_pdf'),
                     InlineKeyboardButton("Get cropped PDF", callback_data='cropped_pdf')],
                    [InlineKeyboardButton("Get originals PDF", callback_data='originals_pdf')],
                    [InlineKeyboardButton("Delete images", callback_data='delete')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Images processed! Choose one option:", reply_markup=reply_markup)

    else:
        update.message.reply_text(NO_IMAGES_MSG)


def pdf_handler(bot, update):
    chat_id = update.effective_chat['id']
    if user_has_images(chat_id):
        pdf_path = get_originals_pdf(chat_id)
        bot.send_document(chat_id=chat_id, document=open('%s' % str(pdf_path), 'rb'), timeout=DOCUMENT_TIMEOUT)
        keyboard = [[InlineKeyboardButton("Delete images from server", callback_data='delete')], ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Images processed! Choose one option:", reply_markup=reply_markup)
    else:
        update.message.reply_text(NO_IMAGES_MSG)


def error(bot, update, error):
    """Log Errors caused by Updates."""

    logger.warning('Update caused error "%s"', error)
    # logger.warning('Update "%s" caused error "%s"', update, error)


def send_originals_pdf(bot, chat_id):
    if user_has_images(chat_id):
        pdf_path = get_originals_pdf(chat_id)
        bot.send_document(chat_id=chat_id, document=open('%s' % str(pdf_path), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Delete images from server", callback_data='delete')], ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Images processed! Choose one option:", reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=chat_id, text=NO_IMAGES_MSG)


def send_cropped_pdf(bot, chat_id):
    if user_has_cropped_images(chat_id):
        pdf_path = get_cropped_pdf(chat_id)
        bot.send_document(chat_id=chat_id, document=open('%s' % str(pdf_path), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Delete images from server", callback_data='delete')], ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Images processed! Choose one option:", reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=chat_id, text="I don't have any cropped images of yours!")


def send_scanned_pdf(bot, chat_id):
    if user_has_scanned_images(chat_id):
        pdf_path = get_scanned_pdf(chat_id)
        bot.send_document(chat_id=chat_id, document=open('%s' % str(pdf_path), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Delete images from server", callback_data='delete')], ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Images processed! Choose one option:", reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=chat_id, text="I don't have any scanned images of yours!")


def delete_inline(bot, chat_id):
    deleted = delete_images_for_user(chat_id)
    reply_markup = ReplyKeyboardRemove()
    if deleted:
        bot.send_message(chat_id=chat_id, text="Your images are gone from my server!", reply_markup=reply_markup)
    else:
        bot.send_message(chat_id=chat_id, text="I don't have any of your images!", reply_markup=reply_markup)


def scan_cropped_inline(bot, chat_id):
    if user_has_scanned_images(chat_id):
        bot.send_message(chat_id=chat_id, text="Started scanning (it may take up to 30 seconds per image)!")
        shrink_cropped(chat_id)
        scanned = get_scanned_images(chat_id)

        for img in scanned:
            bot.send_document(chat_id=chat_id, document=open('%s' % str(img), 'rb'), timeout=DOCUMENT_TIMEOUT)

        keyboard = [[InlineKeyboardButton("Get scanned PDF", callback_data='scanned_pdf')],
                    [InlineKeyboardButton("Get originals PDF", callback_data='originals_pdf')],
                    [InlineKeyboardButton("Delete images", callback_data='delete')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text="Images processed! Choose one option:", reply_markup=reply_markup)

    else:
        bot.send_message(chat_id=chat_id, text="I don't have any cropped images of yours!")


def button(bot, update):
    query = update.callback_query
    chat_id = update.effective_chat['id']
    if query.data == 'cropped_pdf':
        send_cropped_pdf(bot, chat_id)
    if query.data == 'originals_pdf':
        send_originals_pdf(bot, chat_id)
    if query.data == 'scanned_pdf':
        send_scanned_pdf(bot, chat_id)
    if query.data == 'delete':
        delete_inline(bot, chat_id)
    if query.data == 'scan_cropped':
        scan_cropped_inline(bot, chat_id)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(BOTTOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("scan", scan_handler))
    dp.add_handler(CommandHandler("find", find_handler))
    dp.add_handler(CommandHandler("pdf", pdf_handler))
    dp.add_handler(CommandHandler("find_and_scan", find_and_scan_handler))
    dp.add_handler(CommandHandler("delete", delete_handler))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text_handler))
    dp.add_handler(MessageHandler(Filters.photo, image))
    dp.add_handler(MessageHandler(Filters.document, handle_file))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()