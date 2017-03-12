from selenium import webdriver
import time
import requests
import glob
import pandas as pd
import os
import re
import sqlite3
from bs4 import BeautifulSoup
from mozscape import Mozscape
from creds import user, password, client
import shutil

class grab_da():

    def __init__(self, domain):
        mozMetrics = client.urlMetrics(domain)
        self.da = mozMetrics['pda']

    def authority(self):
        return self.da


# chromeOptions = webdriver.ChromeOptions()
# #prefs = {"download.default_directory" : "C:\\Users\\william.cecil\\Desktop\\RawBacklinks"}
# prefs = {"download.default_directory" : "/users/willcecil/desktop/search-console/raw-backlinks/"} # Working on MAC OS
# chromeOptions.add_experimental_option("prefs",prefs)
# driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=chromeOptions)

projects = [line.rstrip('\n') for line in open(r'links.txt')]
login_url = 'https://www.google.com/webmasters/tools/'

db = sqlite3.connect('data.db')
cursor = db.cursor()

url_part1 = 'https://www.google.com/webmasters/tools/external-links-domain?hl=en&siteUrl='

def create_tables(db, cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns(Project TEXT,
                           Links TEXT PRIMARY KEY, Domain TEXT, First_discovered TEXT, Live TEXT, Anchor TEXT, DA INTEGER)''')
    db.commit()

class url_builder():

    def __init__(self,project):
        self.url = '{}{}'.format(url_part1,project)

    def url(self):
        return self.url

def login():
    driver.get(login_url)
    time.sleep(5)
    driver.find_element_by_id('Email').send_keys(user)
    driver.find_element_by_id('next').click()
    time.sleep(2)
    driver.find_element_by_id('Passwd').send_keys(password)
    driver.find_element_by_id('signIn').click()
    time.sleep(10)
    return driver.page_source

def get_links():
    for project in projects:
        download = url_builder(project)
        furl = download.url
        driver.get(furl)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="download-container-2"]/div').click()
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="external-links-domain"]/div[7]/div[3]/button[1]').click()

def store_links(downloads):
    for file in downloads:
        name = re.sub('/users/willcecil/desktop/search-console/raw-backlinks/','',file)
        name = re.sub(r'_.*','',name)
        df = (pd.read_csv(file))
        df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)
        df['Project'] = name
        df['Domain'] = df['Links']
        df['Domain'] = df['Domain'].str.replace(r'(http|https)://', '').astype('str')
        df['Domain'] = df['Domain'].str.replace(r'/.*', '').astype('str')
        df['DA'] = 0
        df['Live'] = 'NAN'
        df['Anchor'] = 'NAN'
        print(df[:10])
        num_rows = len(df)
        # Iterate one row at a time
        for i in range(num_rows):
            try:
                # Try inserting the row
                df.iloc[i:i + 1].to_sql(name="campaigns", con=db, if_exists='append', index=False)
            except:
                # Ignore duplicates
                #print('NO')
                pass

def process_insights(project):
    Project = re.sub('(http://|https://)','',project)
    Project = re.sub('\.', '-', Project)
    Project = re.sub('/', '', Project)
    print(Project)
    d = cursor.execute('SELECT LINKS FROM CAMPAIGNS WHERE Project = "{c}" AND LIVE = "NAN"'.format(c=Project))
    links = d.fetchall()
    links = [x[0] for x in links]
    for link in links:
        try:
            print('Loading ' + link)
            r = requests.get(link)
            soup = BeautifulSoup(r.text, 'html')
            page_links = soup.find_all('a')
            count = 0
            for i in page_links:
                if i['href'].find(project) != -1:
                    status = 'Yes'
                    anchor = i.text
                    cursor.execute(
                        'UPDATE CAMPAIGNS SET Live = "{a}", Anchor = "{d}" WHERE LINKS = "{c}"'.format(a=status, c=link,
                                                                                                       d=anchor))
                    db.commit()
                    count = count + 1
                    break
            if count == 0:
                cursor.execute('UPDATE CAMPAIGNS SET Live = "{a}", Anchor = "{d}" WHERE LINKS = "{c}"'.format(a='No', c=link,d='None'))
                db.commit()
        except:
            cursor.execute('UPDATE CAMPAIGNS SET Live = "{a}", Anchor = "{d}" WHERE LINKS = "{c}"'.format(a='No', c=link,d='None'))
            db.commit()
            continue

    domains = cursor.execute('SELECT DISTINCT DOMAIN FROM CAMPAIGNS WHERE DA = 0')
    domains = domains.fetchall()
    domains = [x[0] for x in domains]

    for domain in domains:
        print(domain)
        da = grab_da(domain)
        final = da.authority()
        print(str(final))
        cursor.execute('UPDATE CAMPAIGNS SET DA = "{a}" WHERE DOMAIN = "{c}"'.format(a=final, c=domain))
        db.commit()
        time.sleep(10)

def archive_downloads(downloads):
    destination = '/users/willcecil/desktop/search-console/archived/'
    for file in downloads:
        shutil.move(file, destination)

def main():
    create_tables(db,cursor)
    #login()
    #get_links()
    #time.sleep(60)
    downloads = glob.glob('/users/willcecil/desktop/search-console/raw-backlinks/*.csv')
    store_links(downloads)
    for project in projects:
        process_insights(project)
    archive_downloads(downloads)

main()