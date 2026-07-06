import unittest
from datetime import datetime
from BeautifulReport import BeautifulReport
from base.project_path import report_path

def run(py_name):
    a = None
    b = None
    if py_name == "test_shanghu.py":
        a = 'shanghu'
        b = '商户后台测试用例'
    elif py_name == "test_xinlian.py":
        a = 'xinlian'
        b = 'C端测试用例'
    elif py_name == "test_houtai.py":
        a = 'houtai'
        b = '管理后台测试用例'
    elif py_name == 'test_case.py':
        a = 'case'
        b = '心链项目测试用例'
    suite_tests = unittest.defaultTestLoader.discover(".", pattern=py_name, top_level_dir=None, )
    report_output_dir = report_path()
    now = datetime.now().strftime('%Y-%m-%d %H：%M：%S')
    filename = a + str(now)
    BeautifulReport(suite_tests).report(description=b, filename=filename, log_path=str(report_output_dir))

if __name__ == '__main__':
    run("test_shanghu.py")
