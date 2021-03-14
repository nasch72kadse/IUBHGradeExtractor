#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import parse_yaml, get_user_state_from_database, get_current_grade_page, content_changed, create_user_in_database, set_user_password_to_database, set_user_name_to_database
import telebot
from threading import Thread

# Init variables
yaml_path = "config/config.yaml"

# Initialize base objects
yaml_object = parse_yaml(yaml_path)
bot = telebot.TeleBot(yaml_object['telegram_token'])


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
        content_has_changed = content_changed(grade_page)
        if content_has_changed:
            bot.reply_to(message, "New grades were published!")
        else:
            bot.reply_to(message, "No new grades were published")
    else:
        bot.reply_to(message, "First register your IUBH user with /enterdata")


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


bot.polling()





