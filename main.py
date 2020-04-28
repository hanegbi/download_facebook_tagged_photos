import os
import regex
import time
import threading
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Facebook:
    URL = 'https://www.facebook.com/'
    USER_NAME = "//*[@id='u_0_a']/div[1]/div[1]/div/a"
    NEXT_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/a[2]'
    PHOTO_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/img'
    PHOTO_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/img'
    VIDEO_ELEMENT = 'videoStageContainer'

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--mute-audio")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('start-maximized')
        self.options.add_argument('--disable-notifications')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.URL)
        self.wait = WebDriverWait(self.driver, 1)
        self.photos_count = 0

    def log_in(self, email, password):
        email_ele = self.driver.find_element(By.NAME, 'email')
        email_ele.clear()
        email_ele.send_keys(email)
        password_ele = self.driver.find_element(By.NAME, 'pass')
        password_ele.clear()
        password_ele.send_keys(password)
        password_ele.send_keys(Keys.RETURN)
        time.sleep(3)

    def _get_username(self):
        username_class = self.driver.find_element(By.XPATH, self.USER_NAME)
        return username_class.get_attribute('href').replace(self.URL, '')

    def _scroll_down(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _create_photos_src_list(self):
        time.sleep(2)
        src_list = []
        photo_id = 1
        while photo_id <= self.photos_count:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, self.VIDEO_ELEMENT)))
            except:
                img = self.wait.until(ec.presence_of_element_located((By.XPATH, self.PHOTO_ELEMENT)))
                src = img.get_attribute('src')
                src_list.append(src)
                print(f'{photo_id}\t{src}')
                photo_id += 1
            finally:
                next_photo = self.driver.find_element(By.XPATH, self.NEXT_ELEMENT)
                next_photo.click()
        return src_list

    @staticmethod
    def _create_folder():
        try:
            os.mkdir('photos')
        except:
            pass

    def _download_photo(self, src, photo_id):
        urllib.request.urlretrieve(src, f'photos/{self.photos_count - photo_id + 1}_facebook_photos_of_me.jpg')
        print(f'{photo_id} of {self.photos_count} photos downloaded')

    def _download_all_photos(self, src_list):
        for photo_id, src in enumerate(src_list, start=1):
            threading.Thread(target=self._download_photo, args=(src, photo_id,)).start()

    def download_photos_of_me(self):
        self.driver.get(self.URL + self._get_username() + '/photos')
        self._scroll_down()
        self.photos_count = len(self.driver.find_elements(By.CLASS_NAME, 'uiMediaThumbImg'))
        print(f'You got {self.photos_count} to be downloaded')
        self.driver.find_element_by_class_name('uiMediaThumbImg').click()
        src_list = self._create_photos_src_list()
        self.driver.quit()
        self._create_folder()
        self._download_all_photos(src_list)


def input_credentials():
    while True:
        email = input('Email: ')
        password = input('Passowrd: ')
        if regex.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) or len(password) > 6:
            break
        print("Invalid syntax, try again")
    return email, password


if __name__ == '__main__':
    email, password = input_credentials()
    fb = Facebook()
    fb.log_in(email, password)
    fb.download_photos_of_me()
    print("test")
