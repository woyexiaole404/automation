# import pytest  #pytest的跳过方法
# @pytest.mark.dependency()
# @pytest.mark.dependency(depends=["test_shouye1"])
# pytest.main(["-s"])
# from base.base import Tool
# Tool.select("SELECT code FROM recharge.system_sms WHERE mobile LIKE '%18983359062%' LIMIT 0, 1000")

# import pyautogui
#
# # 移动鼠标到屏幕上坐标为(x=100, y=100)的位置
# pyautogui.moveTo(100, 100)
#
# # 在指定位置单击鼠标
# pyautogui.click()
import time
import unittest
import minium


class test(minium.MiniTest):
    def test_my(self):
        ##元素定位+点击
        time.sleep(3)
        self.page.get_element("view", inner_text="我的抵用金").click()
        time.sleep(3)
        self.page.get_element("[data-event-opts='tap,jumpUse,$event']").click()
        ##页面跳转
        # self.app.navigate_to("/pages/userCenter/userCenter")


if __name__ == '__main__':
    unittest.main()

# import os
# import time
# import unittest
# from page_object.index_page import shanghu
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from base.base import BasePage
# from BeautifulReport import BeautifulReport
# class Testshanghu(unittest.TestCase):
#
#
# class MysqlData:
#     def __init__(self):
#         self._code = None
#
#     @staticmethod
#     def get_code(mobile):
#         try:
#             sql = "SELECT code FROM recharge.system_sms WHERE mobile = %s"
#             result = Tool.get(sql, (mobile))
#             code = result[0]['code']
#         except Exception as e:
#             print('手机号：' + mobile + ' 未找到对应的验证码', e)
#             return None
#         self._code = code
#
#     def get_stored_code(self):
#         return self._code


# from base.base import Tool
# # from data.mysql_data import MysqlData
# # x = MysqlData.get_code('18983359062')
# # print(x)
# Tool.get("SELECT code FROM recharge.system_sms WHERE mobile = %s ORDER BY created_at DESC LIMIT 1",'18983359062')

# elif py_name == 'test_lhcz.py':
# a = 'lhcz'
# b = '联合成长测试用例'
# import time
# import unittest
# import requests
#
# def get_current_timestamp():  #获取当前时间的时间搓
#     timestamp = int(time.time())
#     return timestamp * 1000  # Convert seconds to milliseconds
#
# class Testshanghu(unittest.TestCase):
#
#     def test_chuangjian(self):
#
#         a = '{"success":true,"message":"请求成功","code":200,"data":[]}'
#         new_data = {'ids': [200]}
#         head = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJkZWZhdWx0XzY0MzY3ZjI1MmU2M2Q2LjY1NjEzODEzIiwiaWF0IjoxNjgxMjkzMDkzLjE5MDAzMywibmJmIjoxNjgxMjkzMDkzLjE5MDAzMywiZXhwIjoxNjgxMzIxODkzLjE5MDAzMywiaWQiOjEsInVzZXJuYW1lIjoic3VwZXJBZG1pbiIsInVzZXJfdHlwZSI6IjEwMCIsIm5pY2tuYW1lIjoi5Yib5aeL5Lq6IiwicGhvbmUiOiIxNjg1ODg4ODk4OCIsImVtYWlsIjoiYWRtaW5AYWRtaW5taW5lLmNvbSIsImF2YXRhciI6bnVsbCwic2lnbmVkIjoi5bm_6ZiU5aSp5Zyw77yM5aSn5pyJ5omA5Li6IiwiZGFzaGJvYXJkIjoic3RhdGlzdGljcyIsInN0YXR1cyI6MSwibG9naW5faXAiOiIxOTIuMTY4LjYuMjA3IiwibG9naW5fdGltZSI6IjIwMjMtMDQtMTIgMTE6MTg6MzkiLCJiYWNrZW5kX3NldHRpbmciOnsibW9kZSI6ImxpZ2h0IiwidGFnIjpmYWxzZSwibWVudUNvbGxhcHNlIjpmYWxzZSwibWVudVdpZHRoIjoyMDAsImxheW91dCI6ImNsYXNzaWMiLCJza2luIjoibWluZSIsImxhbmd1YWdlIjoiemhfQ04iLCJhbmltYXRpb24iOiJtYS1zbGlkZS1kb3duIiwiY29sb3IiOiIjMTY1REZGIn0sImNyZWF0ZWRfYnkiOjAsInVwZGF0ZWRfYnkiOjEsImNyZWF0ZWRfYXQiOiIyMDIzLTAyLTA4IDIyOjIwOjIzIiwidXBkYXRlZF9hdCI6IjIwMjMtMDQtMTIgMTE6MTg6MzkiLCJyZW1hcmsiOm51bGwsInFyX2NvZGUiOiIiLCJzaWduIjoiNDEyNjBiZGM2NzkyYzk5Y2YxZjg1MTE0MTY1MTVjMWYiLCJqd3Rfc2NlbmUiOiJkZWZhdWx0In0.2CeGRch5QCPtR77S_TyJWddFmDm742lyHTG38_Zd1mM' }
#         # 拼接url
#         new_url = 'http://192.168.5.9:2800/prod/product/delete'
#         sion = requests.session()
#         # 向服务器发起请求
#         res = sion.delete(url=new_url,
#                         headers=head,
#                         data=new_data).text
#         print('删除商品返回：', res)
#         self.assertIn(a,res)
#         # return res
# if __name__ == '__main__':
#     unittest.main()
