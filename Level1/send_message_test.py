# -*- coding: utf-8 -*-
"""
Level 1 — Data-driven Send Message test for Mount Orange (Moodle Demo).
All site URLs and element locators are hardcoded in this script.
Only the test data (recipient, message, expected) is read from CSV.
"""
import csv
import os
import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

DATA_FILE = os.path.join(os.path.dirname(__file__), "send_message_data.csv")


def _expand(text, length):
    """Return text if length is 0, otherwise 'a' repeated `length` times."""
    return text if int(length) == 0 else "a" * int(length)


def _load_rows():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class SendMessageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(ChromeDriverManager().install())
        cls.driver.implicitly_wait(30)
        cls._login()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def _login(cls):
        d = cls.driver
        d.get("https://school.moodledemo.net/")
        d.find_element_by_link_text(u"Log in").click()
        d.find_element_by_id("username").send_keys("student")
        d.find_element_by_id("password").send_keys("moodle26")
        d.find_element_by_id("loginbtn").click()

    def _open_conversation(self, recipient_id):
        d = self.driver
        d.get("https://school.moodledemo.net/my/courses.php")
        d.find_element_by_css_selector("a[id^='message-drawer-toggle-'] i").click()
        d.find_element_by_xpath("//div[@id='view-overview-messages-toggle']/button").click()
        d.find_element_by_css_selector("a[data-conversation-id='%s']" % recipient_id).click()

    def _send_message(self, message):
        d = self.driver
        ta = d.find_element_by_css_selector("textarea[data-region='send-message-txt']")
        d.execute_script(
            "var el=arguments[0], v=arguments[1]; "
            "if (el.maxLength && el.maxLength > 0) v = v.substring(0, el.maxLength); "
            "el.value=v; "
            "el.dispatchEvent(new Event('input', {bubbles:true}));",
            ta, message,
        )
        d.execute_script(
            "arguments[0].click();",
            d.find_element_by_css_selector("button[data-action='send-message']"),
        )

    def _last_sent_text(self):
        return self.driver.find_element_by_xpath(
            "(//div[@data-region='message' and contains(@class,' send ')])[last()]//p"
        ).text

    def _last_textarea_value(self):
        return self.driver.find_element_by_css_selector(
            "textarea[data-region='send-message-txt']"
        ).get_attribute("value")


def _make_test(row):
    test_id = row["test_id"]
    recipient_id = row["recipient_id"]
    message = _expand(row["message"], row["length"])
    expected = _expand(row["expected"], row["expected_length"])

    def test(self):
        self._open_conversation(recipient_id)
        if message == "":
            # Empty-send case: click send with nothing typed; textarea should stay empty.
            self.driver.execute_script(
                "arguments[0].click();",
                self.driver.find_element_by_css_selector("button[data-action='send-message']"),
            )
            time.sleep(2)
            self.assertEqual(expected, self._last_textarea_value(),
                             "%s: textarea value mismatch" % test_id)
        else:
            self._send_message(message)
            time.sleep(5)
            self.assertEqual(expected, self._last_sent_text(),
                             "%s: sent message mismatch" % test_id)

    test.__name__ = "test_" + test_id.replace("-", "_")
    return test


for _row in _load_rows():
    setattr(SendMessageTest, "test_" + _row["test_id"].replace("-", "_"), _make_test(_row))


if __name__ == "__main__":
    unittest.main(verbosity=2)
