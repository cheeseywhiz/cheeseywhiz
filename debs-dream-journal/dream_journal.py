#!/usr/bin/env python3
import contextlib
import datetime
import os
import sqlite3
import sys
import textwrap
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException, NoSuchElementException

DATABASE_FILENAME = 'dream_journal.sql'
CREDENTIALS_FNAME = 'credentials.txt'
SLACK_URL = 'https://debsfw22-23.slack.com/'


class DbCommands:
    create_posts = textwrap.dedent('''\
        CREATE TABLE IF NOT EXISTS posts (
            time TEXT NOT NULL,
            text TEXT NOT NULL,
            PRIMARY KEY (time)
        )''')

    init_posts = (textwrap.dedent('''\
        INSERT OR IGNORE INTO posts (time, text) VALUES
            (?, ?), (?, ?)'''),
        (1661954599.708639,
         "I had a dream last night about this YouTube guy named Guga Foods who enjoys cooking meat in a variety of goofy ways. Anyways in the dream I was seeing like both one of his videos and the parts behind the scenes, there was a warm atmosphere and his family was all in the kitchen teasing him about his wacky ingredients. Just as he said “then we add the Guga’s Rub” It started echoing a ton like when Kanye says rock a fella in last call and I instantly woke up",
         1662037879.593199,
         "had a dream i was covered in cinnamon graham crackers")
    )

    insert_post = lambda time, text: (
        textwrap.dedent('''\
            INSERT INTO posts (time, text) VALUES
                (?, ?)'''),
        (time, text)
    )

    most_recent_time = textwrap.dedent('''\
        SELECT time
        FROM posts
        ORDER BY time DESC
        LIMIT 1''')


@contextlib.contextmanager
def get_db():
    def dict_factory(cursor, row):
        """https://gitlab.eecs.umich.edu/sctodd/eecs-485/-/blob/master/p2-serverside/insta485/model.py"""
        return {
            col[0]: row[idx]
            for idx, col in enumerate(cursor.description)
        }

    db = sqlite3.connect(DATABASE_FILENAME)
    db.row_factory = dict_factory
    db.execute('PRAGMA foreign_keys = ON')

    try:
        yield db
    finally:
        db.commit()
        db.close()


class Slack(Chrome):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def login(self, email, uniqname, password):
        self.get(SLACK_URL)

        # google sign in
        google_button = self.find_element(By.ID, 'google_login_button')
        google_button.click()
        email_box = self.find_element(By.ID, 'identifierId')
        email_box.send_keys(email)
        next_button = self.find_element(By.ID, 'identifierNext')
        next_button.click()

        # umich sso
        uniqname_box = self.wait_for_element(By.ID, 'login')
        uniqname_box.send_keys(uniqname)
        password_box = self.find_element(By.ID, 'password')
        password_box.send_keys(password)
        login_button = self.find_element(By.ID, 'loginSubmit')
        login_button.click()
        duo_iframe = self.find_element(By.ID, 'duo_iframe')
        self.switch_to.frame(duo_iframe)
        device_dropdown = Select(self.wait_for_element(By.NAME, 'device'))
        device_dropdown.select_by_index(0)
        duo_push_button = self.find_element(By.CLASS_NAME, 'auth-button')
        duo_push_button.click()
        continue_button = self.wait_for_element(By.CLASS_NAME, 'VfPpkd-vQzf8d')
        continue_button.click()

        print(f'Successfully logged in as {email}')
        time.sleep(5)

    def navigate_dream_journal(self):
        self.get(SLACK_URL)
        dream_journal_button = self.wait_for_element(By.ID, 'C0401GY56MU')
        dream_journal_button.click()
        time.sleep(1)
        dream_journal_button.click()

        posts = self.get_posts_on_page()
        breakpoint()

    def get_posts_on_page(self):
        text_elements = self.find_elements(By.CSS_SELECTOR, '.c-message_list .c-virtual_list__item .p-rich_text_section')
        posts_elements = [
            element
            for element in self.find_elements(By.CSS_SELECTOR, '.c-message_list .c-virtual_list__item')
            #if Slack.get_element(element, By.CLASS_NAME, 'p-rich_text_section')
            if element.get_attribute('role') == 'listitem'
        ]
        elem = posts_elements[0]
        elem2 = elem.find_elements(By.XPATH, '/*')
        breakpoint()
        #return [
        #    (post.get_attribute('id'), text.text)
        #    for post, text in zip(posts_elements, text_elements)
        #]

    @staticmethod
    def get_element(element, by, id_):
        try:
            element.find_element(by, id_)
        except NoSuchElementException:
            return None

    def wait_for_element(self, by, id_):
        WebDriverWait(self, 30).until(
            expected_conditions.presence_of_element_located((by, id_))
        )
        return self.find_element(by, id_)


def main():
    with open('credentials.txt') as f:
        email, uniqname, password = f.read().splitlines()

    with get_db() as db:
        db.execute(DbCommands.create_posts)
        db.execute(*DbCommands.init_posts)

    options = Options()
    options.add_argument('user-data-dir=/Users/sct/Desktop/cheeseywhiz/debs-dream-journal/profile')
    slack = Slack(options=options)
    #slack.login(email, uniqname, password)
    slack.navigate_dream_journal()


if __name__ == '__main__':
    main()
