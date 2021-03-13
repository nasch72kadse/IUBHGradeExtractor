from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import parse_yaml, create_connection_object
import time
import os

# Init variables
yaml_path = "config/config.yaml"
base_url = 'https://care-fs.iubh.de/de/#'
grade_url = "https://care-fs.iubh.de/de/pruefungen-im-fernstudium/notenuebersicht.php"
webpage_file = "page.html"


# Initialize base objects
yaml_object = parse_yaml(yaml_path)
connection_object = create_connection_object(yaml_object)

browser = webdriver.Chrome()
browser.get(base_url)

# Set xpath
login_button_xpath = "/html/body/div[2]/nav/div/div[2]/button"
username_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[1]/div/input"
password_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[2]/div/input"
submit_button_xpath = "/html/body/div[2]/div[2]/div[1]/div/div[3]/div/div/div[2]/div[2]/div[2]/form/div[4]/div/button"

# Click login
loginButton = browser.find_element_by_xpath(login_button_xpath)
loginButton.click()
time.sleep(2)

# Get input elements
username_element = browser.find_element_by_xpath(username_xpath)
password_element = browser.find_element_by_xpath(password_xpath)

# Send login data
username_element.send_keys(connection_object.username)
password_element.send_keys(connection_object.password)

# Click submit
submitButton = browser.find_element_by_xpath(submit_button_xpath)
submitButton.click()

# Load grade overview
browser.get(grade_url)

# Download html page
content = browser.page_source

# ToDo only extract tables (grades)

if os.path.isfile(webpage_file):
    with open(webpage_file, "r") as f:
        data = f.read()
        if data == content:
            # Nothing changed
            pass
        else:
            # Something changed
            print("HDASDA")
# In every case, (over)write the file with the new content
with open(webpage_file, "w") as html_file:
    html_file.write(content)



