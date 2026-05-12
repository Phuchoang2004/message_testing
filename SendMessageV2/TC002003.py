# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
import unittest, time, re

class TC002003(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_t_c002003(self):
        driver = self.driver
        driver.get("https://school.moodledemo.net/")
        driver.find_element_by_link_text(u"Log in").click()
        driver.find_element_by_id("username").send_keys("student")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys("moodle26")
        driver.find_element_by_id("loginbtn").click()
        driver.get("https://school.moodledemo.net/my/courses.php")
        driver.find_element_by_css_selector("a[id^='message-drawer-toggle-'] i").click()
        driver.find_element_by_xpath("//div[@id='view-overview-messages-toggle']/button/span[3]").click()
        driver.find_element_by_css_selector("a[data-conversation-id='3']").click()
        driver.find_element_by_css_selector("textarea[data-region=\"send-message-txt\"]").click()
        driver.find_element_by_css_selector("textarea[data-region='send-message-txt']").clear()
        driver.find_element_by_css_selector("textarea[data-region='send-message-txt']").send_keys("hi")
        driver.execute_script("arguments[0].click();", driver.find_element_by_css_selector("button[data-action='send-message']"))
        time.sleep(5)
        try: self.assertEqual("hi", driver.find_element_by_xpath("(//div[@data-region='message' and contains(@class,' send ')])[last()]//p").text)
        except AssertionError as e: self.verificationErrors.append(str(e))
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
