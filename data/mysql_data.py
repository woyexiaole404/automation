import datetime
from base.base import Tool

class MysqlData:
    @staticmethod
    def get_code(mobile):  #获取验证码
        try:
            sql = "SELECT code FROM recharge.system_sms WHERE mobile = %s ORDER BY created_at DESC LIMIT 1"
            result = Tool.select(sql, mobile)
            return result[0][0]
        except Exception as e:
            print('手机号：' + mobile + ' 未找到对应的验证码或者出现异常', e)