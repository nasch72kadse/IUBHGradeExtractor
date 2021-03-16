#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import parse_yaml, get_user_state_from_database, get_current_grade_page, content_changed, \
    create_user_in_database, set_user_password_to_database, set_user_name_to_database, get_all_registered_users, \
    get_current_grades_as_images
from RepeatedFunction import RepeatedFunction
import telebot
import os

# Init variables
yaml_path = "config/config.yaml"

# Initialize base objects
yaml_object = parse_yaml(yaml_path)
bot = telebot.TeleBot(yaml_object['telegram_token'])


def send_update():
    user_list = get_all_registered_users()
    for chat_id in user_list:
        grade_page = get_current_grade_page(chat_id)
        content_has_changed = content_changed(grade_page, chat_id)
        if content_has_changed:
            bot.send_message(chat_id, "New grades are online!")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Use /enterdata to enter your user information")


@bot.message_handler(commands=['enterdata'])
def enter_data(message):
    chat_id = message.chat.id
    create_user_in_database(chat_id)
    bot.reply_to(message, "Send me your username!")


@bot.message_handler(commands=['newgrades'])
def check_new_grades(message):
    chat_id = message.chat.id
    state = get_user_state_from_database(chat_id)
    if state == 'registered':
        grade_page = get_current_grade_page(chat_id)
        content_has_changed = content_changed(grade_page, chat_id)
        if content_has_changed:
            bot.reply_to(message, "New grades were published!")
        else:
            bot.reply_to(message, "No new grades were published")
    else:
        bot.reply_to(message, "First register your IUBH user with /enterdata")


@bot.message_handler(commands=['getgrades'])
def get_grades(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Gathering data...")
    grade_page = get_current_grade_page(chat_id)
    image_path_list = get_current_grades_as_images(grade_page)
    if image_path_list:
        for image_path in image_path_list:
            with open(image_path, 'rb') as photo:
                bot.send_photo(chat_id, photo)
            os.remove(image_path)
    else:
        bot.send_message(chat_id, "You have no grades yet.")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    chat_id = message.chat.id
    state = get_user_state_from_database(chat_id)
    if state == 'enter_username':
        set_user_name_to_database(chat_id, message.text)
        bot.reply_to(message, "Send me your password!")
    elif state == 'enter_password':
        set_user_password_to_database(chat_id, message.text)
        bot.reply_to(message, "Great you are now registered!")
    else:
        pass


# Call the function every 30 minutes
grade_checker = RepeatedFunction(1800, send_update)

bot.polling()
