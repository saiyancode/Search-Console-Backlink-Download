from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import os

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\william.cecil\\Desktop\\Backlinks"}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=chromeOptions)
#driver = webdriver.PhantomJS(executable_path="phantom\\bin\phantomjs")

projects = [line.rstrip('\n') for line in open(r'links.txt')]
user = 'XXXX'
password = 'XXXX'
login_url = 'https://www.google.com/webmasters/tools/'

def login():
    driver.get(login_url)
    time.sleep(5)
    driver.find_element_by_id('Email').send_keys(user)
    driver.find_element_by_id('next').click()
    time.sleep(2)
    driver.find_element_by_id('Passwd').send_keys(password)
    driver.find_element_by_id('signIn').click()
    time.sleep(10)

def get_links():
    for a in projects:
        driver.get(a)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="download-container-2"]/div').click()
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="external-links-domain"]/div[7]/div[3]/button[1]').click()

def main():
    login()
    get_links()

main()