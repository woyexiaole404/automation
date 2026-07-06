from datetime import datetime
import pymysql
import time
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By

def connect_mysql():
    connect = pymysql.Connect(
        host='47.101.223.148',
        port=3306,
        user='admin2',
        passwd='hy213456',
        db='recharge',
        charset='utf8'
    )
    return connect

class Tool:
    @staticmethod
    def select(sql,args):
        connect = connect_mysql()
        # 获取游标
        cursor = connect.cursor()
        # 执行sql
        cursor.execute(sql,args=args)
        myresult = cursor.fetchall()  # fetchall() 获取所有记录
        connect.close()
        return myresult

    @staticmethod
    def update(sql):
        connect = connect_mysql()
        cursor = connect.cursor()  # 获取游标
        cursor.execute(sql)  # 执行sql语句
        connect.commit()  # 执行update操作时需要写这个，否则就会更新不成功
        result = cursor.fetchone()
        connect.close()
        return result

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def driver_url(self): #获取当前页面url
        return self.driver.current_url

    def go_url(self, url):
        self.driver.get(url)

    def find(self, xpath, by=By.XPATH):
        element = self.driver.find_element(by, xpath)
        return element

    def click_id_element(self, element_id):
        self.find(element_id, by=By.ID).click()

    def click_css_element(self, css):
        self.find(css, By.CSS_SELECTOR).click()

    def click_element(self, xpath):
        self.find(xpath).click()

    def send_element(self, xpath, input_txt):
        self.find(xpath).send_keys(input_txt)

    def clear_element(self, xpath):
        self.find(xpath).clear()

    def clear_backspace(self, xpath):  # 用退格的方式清空输入框
        self.find(xpath).send_keys(Keys.CONTROL + 'a')
        self.find(xpath).send_keys(Keys.BACKSPACE)

    def scroll_bottom_page(self):  # 滑动页面至底部
        js_bottom = "window.scrollTo(0,document.body.scrollHeight)"
        self.driver.execute_script(js_bottom)

    def scroll_top_page(self):  # 滑动页面至顶部
        data = "var q=document.documentElement.scrollTop=0"
        self.driver.execute_script(data)

    def scroll_page(self, step_length):  # 页面滑动指定像素
        self.driver.execute_script("window.scrollBy(0,{})".format(step_length))

    def switch_frame(self, xpath):
        self.driver.switch_to.frame(self.find(xpath))

    def switch_default(self):
        self.driver.switch_to.default_content()

    def mouse_hover(self, xpath):  # 鼠标悬浮
        element_text = self.find(xpath)
        action = ActionChains(self.driver)
        action.move_to_element(element_text)
        action.perform()
        time.sleep(2)

    def mouse_hover_id(self, element_id):  # 鼠标悬浮  通过元素id
        element_text = self.find(element_id, by=By.ID)
        action = ActionChains(self.driver)
        action.move_to_element(element_text)
        action.perform()
        time.sleep(2)

    def mouse_hover_css(self, css):  # 鼠标悬浮  通过css定位
        element_text = self.find(css, by=By.CSS_SELECTOR)
        action = ActionChains(self.driver)
        action.move_to_element(element_text)
        action.perform()
        time.sleep(2)

    def get_txt(self, xpath):
        return self.find(xpath).get_attribute('textContent')

    def click_js(self, xpath):
        ele = self.find(xpath)
        self.driver.execute_script('arguments[0].click()', ele)

    def get_handles(self): #打开新标签
        handles = self.driver.window_handles
        return handles

    def switch_to_handles(self, handles): #打开新标签
        self.driver.switch_to.window(handles)

    def maximize(self):
        self.driver.maximize_window()

    def get_elements_num(self, value):
        res = self.driver.find_elements(By.XPATH, value)
        num = len(res)
        return num

    def checkbox_status(self, xpath):
        checked = self.find(f'{xpath}').is_selected()
        return checked

    def refresh(self):
        self.driver.refresh()

    def get_attribute_value(self, xpath, key):  # 获取属性值
        return self.find(xpath).get_attribute(key)
