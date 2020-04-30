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
    PHOTO_THUMB_ELEMENT = 'img.opwvks06.hop1g133.linmgsc8.t63ysoy8.bixrwtb6'
    VIDEO_THUMB_ELEMENT = 'span.oi732d6d.ik7dh3pa.d2edcug0.qv66sw1b.c1et5uql.a8c37x1j.hop8lmos.enqfppq2.e9vueds3' \
                          '.j5wam9gi.knj5qynh.ljqsnud1'
    PHOTO_ELEMENT = 'img.idiwt2bm.d2edcug0.dbpd2lw6'
    NEXT_ELEMENT = '//*[@id="mount_0_0"]/div/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div[1]/div/div[1]/div[' \
                   '2]/div[1]/div[2]/div'
    VIDEO_ELEMENT = 'div.tv7at329.b5wmifdl.pmk7jnqg.kfkz5moi.rk01pc8j.py2didcb.hwaazqwg.kmdw4o4n.l23jz15m.e4zzj2sf' \
                    '.thwo4zme.kr9hpln1 '

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
            time.sleep(2)
            try:
                self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.VIDEO_ELEMENT)))
                time.sleep(3)
            except:
                time.sleep(1)
                img = self.driver.find_element(By.CSS_SELECTOR, self.PHOTO_ELEMENT)
                src = img.get_attribute('src')
                src_list.append(src)
                print(f'{photo_id}\t{src}')
                photo_id += 1
            finally:
                next_photo = self.driver.find_element(By.XPATH, self.NEXT_ELEMENT)
                self.driver.execute_script("arguments[0].click();", next_photo)
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
        self.driver.get(self.URL + 'me/photos')
        self._scroll_down()
        self.photos_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div.b5fwa0m2.pmk7jnqg.plgsh5y4'))
        videos_count = len(self.driver.find_elements(By.CSS_SELECTOR, self.VIDEO_THUMB_ELEMENT))
        self.photos_count = self.photos_count-videos_count
        print(f'You got {self.photos_count} to be downloaded')
        photo_thumb = self.driver.find_element(By.CSS_SELECTOR, self.PHOTO_THUMB_ELEMENT)
        self.driver.execute_script("arguments[0].click();", photo_thumb)
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
