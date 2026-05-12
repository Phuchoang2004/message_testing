# -*- coding: utf-8 -*-
"""
Level 2 — Data-driven Send Message test for Mount Orange (Moodle Demo).
Every URL, credential, and element locator is supplied by the CSV — the
script itself is generic and could be reused for any similar messaging app.

CSV columns:
    test_id, base_url, login_link_text, username_id, username_value,
    password_id, password_value, login_btn_id, courses_url, drawer_toggle,
    private_section, conversation_selector, textarea_selector, send_button,
    verify_xpath, message, length, expected, expected_length

verify_xpath uses '$$' as a comma placeholder (CSV cannot embed a raw comma
inside a quoted xpath without escaping). It is replaced at load time.
"""
import csv
import os
import time
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

DATA_FILE = os.path.join(os.path.dirname(__file__), "send_message_data.csv")


def _expand(text, length):
    return text if int(length) == 0 else "a" * int(length)


def _load_rows():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r.get("verify_xpath"):
            r["verify_xpath"] = r["verify_xpath"].replace("$$", ",")
    return rows


class SendMessageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(ChromeDriverManager().install())
        cls.driver.implicitly_wait(30)
        cls._logged_in = False

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def _login(self, row):
        d = self.driver
        d.get(row["base_url"])
        d.find_element_by_link_text(row["login_link_text"]).click()
        d.find_element_by_id(row["username_id"]).send_keys(row["username_value"])
        d.find_element_by_id(row["password_id"]).send_keys(row["password_value"])
        d.find_element_by_id(row["login_btn_id"]).click()
        type(self)._logged_in = True

    def _open_conversation(self, row):
        d = self.driver
        d.get(row["courses_url"])
        d.find_element_by_css_selector(row["drawer_toggle"]).click()
        d.find_element_by_xpath(row["private_section"]).click()
        d.find_element_by_css_selector(row["conversation_selector"]).click()

    def _send_message(self, row, message):
        d = self.driver
        ta = d.find_element_by_css_selector(row["textarea_selector"])
        d.execute_script(
            "var el=arguments[0], v=arguments[1]; "
            "if (el.maxLength && el.maxLength > 0) v = v.substring(0, el.maxLength); "
            "el.value=v; "
            "el.dispatchEvent(new Event('input', {bubbles:true}));",
            ta, message,
        )
        d.execute_script(
            "arguments[0].click();",
            d.find_element_by_css_selector(row["send_button"]),
        )


def _make_test(row):
    test_id = row["test_id"]
    message = _expand(row["message"], row["length"])
    expected = _expand(row["expected"], row["expected_length"])

    def test(self):
        if not type(self)._logged_in:
            self._login(row)
        self._open_conversation(row)

        if message == "":
            self.driver.execute_script(
                "arguments[0].click();",
                self.driver.find_element_by_css_selector(row["send_button"]),
            )
            time.sleep(2)
            actual = self.driver.find_element_by_css_selector(
                row["textarea_selector"]
            ).get_attribute("value")
            self.assertEqual(expected, actual,
                             "%s: textarea value mismatch" % test_id)
        else:
            self._send_message(row, message)
            time.sleep(5)
            actual = self.driver.find_element_by_xpath(row["verify_xpath"]).text
            self.assertEqual(expected, actual,
                             "%s: sent message mismatch" % test_id)

    test.__name__ = "test_" + test_id.replace("-", "_")
    return test


for _row in _load_rows():
    setattr(SendMessageTest, "test_" + _row["test_id"].replace("-", "_"), _make_test(_row))


if __name__ == "__main__":
    unittest.main(verbosity=2)
