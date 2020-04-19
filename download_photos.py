import urllib.request
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Facebook:
    URL = 'https://www.facebook.com/'
    EMAIL = 'myEmail'
    PASSWORD = 'myPassword'
    NEXT_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/a[2]'
    PHOTO_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/img'
    PHOTO_ELEMENT = '//*[@id="photos_snowlift"]/div[2]/div/div[1]/div[1]/div[1]/div[1]/div[3]/img'
    VIDEO_ELEMENT = 'videoStageContainer'

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.options.add_argument("--mute-audio")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('start-maximized')
        self.options.add_argument('--disable-notifications')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.URL)
        self.wait = WebDriverWait(self.driver, 1)

    def log_in(self):
        email = self.driver.find_element(By.NAME, 'email')
        email.clear()
        email.send_keys(self.EMAIL)
        password = self.driver.find_element(By.NAME, 'pass')
        password.clear()
        password.send_keys(self.PASSWORD)
        password.send_keys(Keys.RETURN)

    def get_username(self):
        username_class = self.driver.find_element(By.XPATH, "//*[@id='u_0_a']/div[1]/div[1]/div/a")
        return username_class.get_attribute('href').replace(self.URL, '')

    def scroll_down(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def create_photos_src_list(self, photo_id, src_list):
        time.sleep(2)
        while photo_id <= self.get_count_photos():
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, self.VIDEO_ELEMENT)))
            except:
                img = self.wait.until(ec.presence_of_element_located((By.XPATH, self.PHOTO_ELEMENT)))
                src = img.get_attribute('src')
                src_list.append(src)
                print(str(photo_id) + '\t' + src)
                photo_id += 1
            finally:
                next_photo = self.driver.find_element(By.XPATH, self.NEXT_ELEMENT)
                next_photo.click()
        return src_list

    def download_photo(self, src, photo_id):
        urllib.request.urlretrieve(src, str(self.get_count_photos() - photo_id + 1) + '_facebook_photos_of_me.jpg')
        print(str(photo_id) + " of " + str(self.get_count_photos()) + " photos downloaded")

    def download_all_photos(self, src_list):
        for photo_id, src in enumerate(src_list, start=1):
            threading.Thread(target=self.download_photo, args=(src, photo_id,)).start()

    @staticmethod
    def get_count_photos():
        return count_photos

    def download_photos_of_me(self):
        self.log_in()
        time.sleep(3)
        self.driver.get(self.URL + self.get_username() + '/photos')
        self.scroll_down()
        global count_photos
        count_photos = len(self.driver.find_elements(By.CLASS_NAME, 'uiMediaThumbImg'))
        print(count_photos)
        self.driver.find_element_by_class_name('uiMediaThumbImg').click()
        src_list = []
        photo_id = 1
        src_list = self.create_photos_src_list(photo_id, src_list)
        self.driver.quit()
        self.download_all_photos(src_list)


if __name__ == '__main__':
    fb = Facebook()
    fb.download_photos_of_me()