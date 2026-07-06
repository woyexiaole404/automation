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
