#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
from connection import GradeConnection
from selenium import webdriver
import time
import os
import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import uuid

# Init variables
base_url = 'https://care-fs.iubh.de/de/#'
grade_url = "https://care-fs.iubh.de/de/pruefungen-im-fernstudium/notenuebersicht.php"
webpage_file = "page.html"


def parse_yaml(yaml_file):
    """
        Parse yaml file to object and return it
        :param: yaml_file: path to yaml file
        :return: yaml_object
    """
    with open(yaml_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return False


def get_current_grade_page(chat_id):
    """
        Get the content of the grading page as an HTML string
        :param: chat_id: ID of the chat (user)
        :return: String with HTML content
    """
    # Get connection parameters
    connection_object = get_connection_from_chat_id(chat_id)
    if connection_object:
        # Initialize browser
        browser = webdriver.Chrome()
        browser.get(base_url)

        # Set xpath
        login_button_xpath = "/html/body/div[2]/nav/div/div[2]/button"
        username_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[1]/div/input"
        password_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[2]/div/input"
        submit_button_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[4]/div/button"

        # Click login
        login_button = browser.find_element_by_xpath(login_button_xpath)
        login_button.click()
        time.sleep(2)

        # Get input elements
        username_element = browser.find_element_by_xpath(username_xpath)
        password_element = browser.find_element_by_xpath(password_xpath)

        # Send login data
        username_element.send_keys(connection_object.username)
        password_element.send_keys(connection_object.password)

        # Click submit
        submit_button = browser.find_element_by_xpath(submit_button_xpath)
        submit_button.click()

        # Load grade overview
        browser.get(grade_url)

        # Download html page
        content = browser.page_source
        return content
    else:
        return None


def content_changed(new_content, chat_id):
    content_has_changed = False
    if os.path.isfile(str(chat_id) + "_" + webpage_file):
        with open(str(chat_id) + "_" + webpage_file, "r", encoding='utf8') as f:
            data = f.read()
            # Convert html tables to dataframes
            old_tables_dataframe = get_iubh_grade_table_dataframes(data)
            new_tables_dataframe = get_iubh_grade_table_dataframes(new_content)
            for index, element in enumerate(old_tables_dataframe):
                if element.equals(new_tables_dataframe[index]):
                    pass
                else:
                    content_has_changed = True
    # In every case, (over)write the file with the new content
    with open(str(chat_id) + "_" + webpage_file, "w", encoding='utf8') as html_file:
        html_file.write(new_content)
    return content_has_changed


def get_iubh_grade_table_dataframes(content_as_html):
    dataframe_list = pd.read_html(content_as_html)
    return dataframe_list


def connect_to_database():
    con = sqlite3.connect('login_data.db')
    return con


def close_connection_to_database(connection):
    connection.commit()
    connection.close()


def create_user_in_database(chat_id):
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Delete entry if existing and create new one
    cursor.execute('REPLACE INTO user VALUES (?,?,?,?)', (chat_id, '', '', 'enter_username'))
    # Close connection
    close_connection_to_database(connection)


def get_user_state_from_database(chat_id):
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Execute SQL query
    cursor.execute('SELECT state FROM user WHERE chat_id=?', (str(chat_id),))
    state = cursor.fetchone()
    if state:
        state = state[0]
    # Close connection
    close_connection_to_database(connection)
    return state


def set_user_name_to_database(chat_id, username):
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Execute SQL query
    cursor.execute('UPDATE user SET username=?, state=? WHERE chat_id=?', (username, 'enter_password', str(chat_id)))
    # Close connection
    close_connection_to_database(connection)


def set_user_password_to_database(chat_id, password):
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Execute SQL query
    cursor.execute('UPDATE user SET password=?, state=? WHERE chat_id=?', (password, 'registered', str(chat_id)))
    # Close connection
    close_connection_to_database(connection)


def get_connection_from_chat_id(chat_id):
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Execute SQL query
    username = cursor.execute('SELECT username FROM user WHERE chat_id=?', (str(chat_id),)).fetchone()
    password = cursor.execute('SELECT password FROM user WHERE chat_id=?', (str(chat_id),)).fetchone()
    # Close connection
    close_connection_to_database(connection)
    if username and password:
        grade_connection = GradeConnection(username[0], password[0])
        return grade_connection
    else:
        return None


def get_all_registered_users():
    """
    Get all chat_ids from users that are registered
    :return: List of chat_ids
    """
    new_user_list = []
    # Create connection
    connection = connect_to_database()
    cursor = connection.cursor()
    # Execute SQL query
    cursor.execute('SELECT chat_id FROM user WHERE state=?', ('registered',))
    user_list = cursor.fetchall()
    for registered_user in user_list:
        new_user_list.append(registered_user[0])
    # Close connection
    close_connection_to_database(connection)
    return new_user_list


def get_current_grades_as_images(html_page):
    dataframe_list = get_iubh_grade_table_dataframes(html_page)
    filtered_dataframe_list = filter_grade_dataframes(dataframe_list)
    image_file_list = get_image_files(filtered_dataframe_list)
    return image_file_list


def filter_grade_dataframes(unfiltered_dataframe_list):
    filtered_dataframe_list = []
    for dataframe in unfiltered_dataframe_list:
        # Only include actual grade tables and tables that have at least one grade
        if "Modul / Lehrveranstaltung" in dataframe.columns and len(dataframe.Bewertung.value_counts()) > 0:
            new_dataframe = dataframe[["Modul / Lehrveranstaltung", "Note", "Bewertung", "Credits", "Datum"]].copy()
            filtered_dataframe_list.append(new_dataframe)
    return filtered_dataframe_list


def get_image_files(grade_dataframes):
    image_name_list = []
    for dataframe in grade_dataframes:
        image_id = str(uuid.uuid4()) + ".png"
        # Plot table and save
        fig = render_mpl_table(dataframe)
        fig.savefig(image_id)
        image_name_list.append(image_id)
    return image_name_list


def render_mpl_table(data, col_width=4.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
    return ax.get_figure()
