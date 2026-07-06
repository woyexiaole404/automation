from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from base.base import BasePage
from base.project_path import img_code_file
import unittest
import ddddocr
from selenium.webdriver.common.by import By
now = datetime.now().strftime('%Y-%m-%d %H：%M：%S')


def get_yzm(self):
    self.driver.find_element(By.CLASS_NAME, 'canvas').screenshot(img_code_file('yanzhengma{}.png'.format(now)))  # 获取验证码图片  并保存在当前目录下 图片名:yanzhengma.png

def draw_yzm(self):     #识别提取验证码
    ocr = ddddocr.DdddOcr()
    with open(img_code_file('yanzhengma{}.png'.format(now)), 'rb' )as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    return res

class Testsaas(unittest.TestCase):

    def setUp(self) -> None:
        self.options = webdriver.ChromeOptions()
        #options.add_experimental_option('detach', True)  # 不自动关闭浏览器
        self.options.add_argument('--start-maximized')  # 窗口最大化
        self.driver = webdriver.Chrome(options=self.options)

    def tearDown(self) -> None:
        self.driver.quit()

    def test_01_login(self):  # 数字控制用例执行顺序
        """正确的账号和密码，登录成功"""
        try:
            BasePage(self.driver).go_url('https://plus.xiwshijieheping.com/')
            time.sleep(5)
            a = '234'
            BasePage(self.driver).click_element('//*[text()="登录"]')
            time.sleep(2)
            BasePage(self.driver).send_element('//*[@id="app"]/div/div[2]/div/div[2]/div/div/div/div[2]/div/input',"dixuan123")
            time.sleep(2)
            BasePage(self.driver).send_element('//*[@id="app"]/div/div[2]/div/div[2]/div/div/div/div[3]/div/input',
                                               "123456")
            time.sleep(2)
            BasePage(self.driver).click_element('//*[@id="app"]/div/div[2]/div/div[2]/div/div/div/div[5]')
            time.sleep(5)
            BasePage(self.driver).click_element('//*[text()="进入应用后台"]')
            time.sleep(10)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            BasePage(self.driver).send_element('//*[@placeholder="请输入应用名称"]',"101")
            time.sleep(2)
            BasePage(self.driver).click_element('//*[@id="app"]/div[1]/div[3]/section/div/div[1]/div[3]/div[2]/div[1]/button')
            time.sleep(2)
            BasePage(self.driver).click_element('//*[@id="2079"]/div[2]/div/img[1]')
            time.sleep(10)
            BasePage(self.driver).click_element('//*[@id="app"]/div[1]/div[1]/div[1]/div[2]/a')
            time.sleep(2)
            BasePage(self.driver).click_element('//*[@aria-controls="pane-componentList"]')
            time.sleep(2)
            b = BasePage(self.driver).get_txt('//*[@id="tab-componentList"]')
            time.sleep(1)
            self.assertIn(a, b)
        except Exception as e:
            print(self.driver.current_url, e)
            time.sleep(2)
            raise

if __name__ == '__main__':
    unittest.main()
