#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils import parse_yaml, create_connection_object, get_current_grade_page, content_changed
import os
from bs4 import BeautifulSoup
import pandas as pd
import telebot

# Init variables
yaml_path = "config/config.yaml"

# Initialize base objects
yaml_object = parse_yaml(yaml_path)
connection_object = create_connection_object(yaml_object)
bot = telebot.TeleBot(connection_object.telegram_token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Guten Tag!")


@bot.message_handler(commands=['newgrades'])
def check_new_grades(message):
    grade_page = get_current_grade_page(connection_object)
    content_has_changed = content_changed(grade_page)
    if content_has_changed:
        bot.reply_to(message, "Neue Noten sind online!")
    else:
        bot.reply_to(message, "Alles wie immer, keine neuen Noten")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()







