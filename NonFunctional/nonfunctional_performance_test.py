# -*- coding: utf-8 -*-
"""
Non-functional test #1 — Performance / Response time.

Type:        Performance (response-time)
Approach:    Send the same short message N times via the message drawer and
             measure the elapsed time between the "Send" click and the moment
             the new bubble becomes visible in the conversation. Report avg
             and p95 latency.
Tool:        Selenium WebDriver + Python's time.perf_counter().
Pass criteria: average < 3.0s, p95 < 5.0s (adjustable).
"""
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ITERATIONS = 10
RECIPIENT_ID = "3"   # Jeffrey Sanders
AVG_LIMIT = 3.0
P95_LIMIT = 5.0


class PerformanceTest(unittest.TestCase):

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
        # If the drawer opened into an existing conversation, click back to overview.
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

    def test_send_message_latency(self):
        self._login()
        self._open_conversation()
        d = self.driver
        wait = WebDriverWait(d, 10)

        timings = []
        for i in range(ITERATIONS):
            msg = "perf-%d-%d" % (i, int(time.time() * 1000))
            ta = d.find_element_by_css_selector("textarea[data-region='send-message-txt']")
            d.execute_script(
                "var el=arguments[0]; el.value=arguments[1]; "
                "el.dispatchEvent(new Event('input', {bubbles:true}));",
                ta, msg,
            )

            start = time.perf_counter()
            d.execute_script(
                "arguments[0].click();",
                d.find_element_by_css_selector("button[data-action='send-message']"),
            )
            wait.until(EC.text_to_be_present_in_element(
                (By.XPATH,
                 "(//div[@data-region='message' and contains(@class,' send ')])[last()]//p"),
                msg,
            ))
            timings.append(time.perf_counter() - start)

        timings.sort()
        avg = sum(timings) / len(timings)
        p95 = timings[int(len(timings) * 0.95) - 1] if len(timings) > 1 else timings[0]
        print("\nPerformance results over %d iterations:" % ITERATIONS)
        print("  avg = %.3fs   p95 = %.3fs   min = %.3fs   max = %.3fs" %
              (avg, p95, timings[0], timings[-1]))

        self.assertLess(avg, AVG_LIMIT, "average latency too high")
        self.assertLess(p95, P95_LIMIT, "p95 latency too high")


if __name__ == "__main__":
    unittest.main(verbosity=2)
