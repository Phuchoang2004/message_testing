# -*- coding: utf-8 -*-
"""
Non-functional test #2 — Load / Throughput.

Type:        Load
Approach:    Send N messages back-to-back to the same conversation and assert
             that every one of them is rendered in the conversation pane.
             Verifies the messaging endpoint can sustain a burst without
             dropping or merging messages.
Tool:        Selenium WebDriver.
Pass criteria: All N messages are visible after the burst completes.
"""
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BURST = 50
RECIPIENT_ID = "3"


class LoadTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(30)

    def tearDown(self):
        self.driver.quit()

    def _login(self):
        d = self.driver
        d.get("https://school.moodledemo.net/")
        d.find_element_by_link_text(u"Log in").click()
        d.find_element_by_id("username").send_keys("student")
        d.find_element_by_id("password").send_keys("moodle26")
        d.find_element_by_id("loginbtn").click()

    def _open_conversation(self):
        d = self.driver
        d.get("https://school.moodledemo.net/my/courses.php")
        d.find_element_by_css_selector("a[id^='message-drawer-toggle-'] i").click()
        time.sleep(1)
        backs = d.find_elements_by_css_selector(
            "[data-region='view-conversation'] a[data-route-back]"
        )
        for b in backs:
            if b.is_displayed():
                d.execute_script("arguments[0].click();", b)
                time.sleep(1)
                break
        d.execute_script(
            "arguments[0].click();",
            d.find_element_by_xpath("//div[@id='view-overview-messages-toggle']/button"),
        )
        time.sleep(1)
        d.find_element_by_css_selector("a[data-conversation-id='%s']" % RECIPIENT_ID).click()

    def test_burst_send(self):
        self._login()
        self._open_conversation()
        d = self.driver
        wait = WebDriverWait(d, 15)

        tag = "load-%d" % int(time.time())
        for i in range(BURST):
            msg = "%s-%d" % (tag, i)
            ta = d.find_element_by_css_selector("textarea[data-region='send-message-txt']")
            d.execute_script(
                "var el=arguments[0]; el.value=arguments[1]; "
                "el.dispatchEvent(new Event('input', {bubbles:true}));",
                ta, msg,
            )
            d.execute_script(
                "arguments[0].click();",
                d.find_element_by_css_selector("button[data-action='send-message']"),
            )

        # Wait for the final message to appear, then verify all of them
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH,
             "(//div[@data-region='message' and contains(@class,' send ')])[last()]//p"),
            "%s-%d" % (tag, BURST - 1),
        ))

        page = d.page_source
        missing = [i for i in range(BURST) if ("%s-%d" % (tag, i)) not in page]
        self.assertEqual([], missing,
                         "Missing %d of %d messages: %s" % (len(missing), BURST, missing))


if __name__ == "__main__":
    unittest.main(verbosity=2)
