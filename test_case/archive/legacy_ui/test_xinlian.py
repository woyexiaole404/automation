import time
import unittest
import platform
from datetime import datetime
from selenium.webdriver.common.by import By
from BeautifulReport.BeautifulReport import HTML_IMG_TEMPLATE
from page_object.index_page import shanghu
from base.base import BasePage, create_chrome_driver
from base.project_path import img_file, test_case_img_dir, test_case_img_file
from BeautifulReport import BeautifulReport
from data.mysql_data import MysqlData

now = datetime.now().strftime('%Y-%m-%d %H：%M：%S')  #报错截图保存名字和测试报告调用截图的名字必须一致

class Testxinlian(unittest.TestCase):
    skip = None  # 先声明 skip 变量
    img_path = test_case_img_dir()  #BeautifulReport报告手动截图使用

    def setUp(self) -> None:
        self.driver = create_chrome_driver()
        self.driver.maximize_window()

    def save_img(self, img_name):  #报错截图
        """
            传入一个img_name, 并存储到自定义的文件路径下
        :param img_name:
        :return:
        """
        # self.driver.get_screenshot_as_file(rf'img/{img_name}.png')  #存储到默认路径下
        self.driver.get_screenshot_as_file(test_case_img_file('{}{}.png'.format(img_name, now)))
        data = BeautifulReport.img2base(self.img_path, img_name+now + '.png')  #在skip和BeautifulReport装饰器冲突的情况下，使用手动截图
        print(HTML_IMG_TEMPLATE.format(data, data))  #BeautifulReport报告会自动把print带入报告

    def step_img(self, img_name):  #步骤截图

        self.driver.get_screenshot_as_file(img_file('{}{}.png'.format(img_name, now)))

    def tearDown(self) -> None:
        self.driver.quit()

    # @BeautifulReport.add_test_img('test_login_01'+now)  #该装饰器和skip冲突，暂时没使用
    def test_01_login1(self):  #数字控制用例执行顺序
        """正确的账号和密码，登录成功"""
        try:
            shanghu(self.driver).login('test234', '123456')
            # a = '心链商户控制台'
            a = '123'
            b = BasePage(self.driver).get_txt('//*[@id="app"]/section/header/div/div[1]/h3')
            time.sleep(1)
            self.step_img('首页1')
            global skip  # 使用 global 声明
            if b == a:
                skip = True
            else:
                skip = False
            self.assertIn(a, b)
        except Exception as e:
            self.save_img('test_01_login1')
            print(self.driver.current_url, e)
            time.sleep(2)
            raise

if __name__ == '__main__':
    unittest.main()
