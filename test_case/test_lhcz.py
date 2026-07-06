from datetime import datetime
import time
from base.base import BasePage, create_chrome_driver
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

class Testlhcz(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = create_chrome_driver()
        self.driver.maximize_window()

    def tearDown(self) -> None:
        self.driver.quit()

    def test_01_login(self):  # 数字控制用例执行顺序
        """正确的账号和密码，登录成功"""
        try:
            BasePage(self.driver).go_url('http://t.qf.baiopen.top/#/login')
            time.sleep(2)
            get_yzm(self)
            code = draw_yzm(self)
            print(code)
            BasePage(self.driver).send_element('//*[@id="app"]/div/div/div/form/div[1]/div/div/div/span/input', '黄飞')
            time.sleep(1)
            BasePage(self.driver).send_element('//*[@id="app"]/div/div/div/form/div[2]/div/div/div/span/input',
                                               '123456')
            time.sleep(1)
            BasePage(self.driver).send_element('//*[@id="app"]/div/div/div/form/div[3]/div/div/div/span/span[1]/input', code)
            time.sleep(2)
            BasePage(self.driver).click_element('//*[@id="app"]/div/div/div/form/div[4]/div/div/div/button')
            time.sleep(2)
            a = '企业服务平台'
            # a = '123'
            b = BasePage(self.driver).get_txt('//*[@id="app"]/main/section/div/div/div[1]/span')
            time.sleep(1)
            self.assertIn(a, b)
        except Exception as e:
            print(self.driver.current_url, e)
            time.sleep(2)
            raise

if __name__ == '__main__':
    unittest.main()
