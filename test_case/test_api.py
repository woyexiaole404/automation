import time
import unittest
import requests

def get_current_timestamp():  #获取当前时间的时间搓
    timestamp = int(time.time())
    return timestamp * 1000  # Convert seconds to milliseconds

class Testshanghu(unittest.TestCase):

    def test_chuangjian(self):

        a = '{"success":true,"message":"请求成功","code":200,"data":[]}'
        new_data = {'ids': [200]}
        head = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJkZWZhdWx0XzY0Mzc1ODU2MzEwZjc0LjEzODg3OTcyIiwiaWF0IjoxNjgxMzQ4Njk0LjIwMDk2NSwibmJmIjoxNjgxMzQ4Njk0LjIwMDk2NSwiZXhwIjoxNjgxMzc3NDk0LjIwMDk2NSwiaWQiOjEsInVzZXJuYW1lIjoic3VwZXJBZG1pbiIsInVzZXJfdHlwZSI6IjEwMCIsIm5pY2tuYW1lIjoi5Yib5aeL5Lq6IiwicGhvbmUiOiIxNjg1ODg4ODk4OCIsImVtYWlsIjoiYWRtaW5AYWRtaW5taW5lLmNvbSIsImF2YXRhciI6bnVsbCwic2lnbmVkIjoi5bm_6ZiU5aSp5Zyw77yM5aSn5pyJ5omA5Li6IiwiZGFzaGJvYXJkIjoic3RhdGlzdGljcyIsInN0YXR1cyI6MSwibG9naW5faXAiOiIxOTIuMTY4LjUuOTUiLCJsb2dpbl90aW1lIjoiMjAyMy0wNC0xMiAxNzo1MTozMyIsImJhY2tlbmRfc2V0dGluZyI6eyJtb2RlIjoibGlnaHQiLCJ0YWciOmZhbHNlLCJtZW51Q29sbGFwc2UiOmZhbHNlLCJtZW51V2lkdGgiOjIwMCwibGF5b3V0IjoiY2xhc3NpYyIsInNraW4iOiJtaW5lIiwibGFuZ3VhZ2UiOiJ6aF9DTiIsImFuaW1hdGlvbiI6Im1hLXNsaWRlLWRvd24iLCJjb2xvciI6IiMxNjVERkYifSwiY3JlYXRlZF9ieSI6MCwidXBkYXRlZF9ieSI6MSwiY3JlYXRlZF9hdCI6IjIwMjMtMDItMDggMjI6MjA6MjMiLCJ1cGRhdGVkX2F0IjoiMjAyMy0wNC0xMiAxNzo1MTozMyIsInJlbWFyayI6bnVsbCwicXJfY29kZSI6IiIsInNpZ24iOiI0MTI2MGJkYzY3OTJjOTljZjFmODUxMTQxNjUxNWMxZiIsImp3dF9zY2VuZSI6ImRlZmF1bHQifQ.CHG437-Qa84yS9umOM7QZusPqc1xkogx8jFMRygvZqI' }
        # 拼接url
        new_url = 'http://192.168.5.9:2800/prod/product/delete'
        sion = requests.session()
        # 向服务器发起请求
        res = sion.delete(url=new_url,
                        headers=head,
                        data=new_data).text
        print('删除商品返回：', res)
        self.assertIn(a,res)
        # return res
if __name__ == '__main__':
    unittest.main()