from base.base import BasePage
import time

class shanghu(BasePage):
    def login(self, username, passwd):
        self.go_url('http://t.webmerchant.baishouopen.com/#/login')
        self.click_element('//*[@id="app"]/div[1]/div[2]/form[1]/div[1]/img')
        time.sleep(2)
        self.send_element('//*[@id="app"]/div[1]/div[2]/form[1]/div[2]/div[2]/div/div[1]/input', username)
        time.sleep(2)
        self.send_element('//*[@id="app"]/div[1]/div[2]/form[1]/div[2]/div[3]/div/div/input', passwd)
        time.sleep(2)
        self.click_element('//*[@id="app"]/div[1]/div[2]/form[1]/div[2]/div[4]/div/button')
        time.sleep(1)

    def wodeyingyong(self, username, passwd):
        self.login(username, passwd)
        self.click_element('//*[@id="app"]/section/section/aside/div/ul/li[1]/div/span')
        time.sleep(2)
        self.click_element('//*[@id="app"]/section/section/aside/div/ul/li[1]/ul/a/li')
        time.sleep(2)





