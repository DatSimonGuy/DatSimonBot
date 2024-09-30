""" Random fun functions that don't fit anywhere else. """

import time
from playwright.async_api import async_playwright
from dsb.main.modules.base_modules.module import Module

class Miscelanious(Module):
    """ Miscelanious module """
    name = "Miscelanious"
    async def is_stos_alive(self) -> float:
        """ Check if stos is alive. Returns ammount of seconds it took to check a simple code. """
        async with async_playwright() as pw:
            firefox = pw.firefox
            browser = await firefox.launch(args=["--disable-cache"])
            page = await browser.new_page()
            stos_page = self._bot.config["stos_page"]
            await page.goto(stos_page)
            login = self._bot.config["stos_login"]
            password = self._bot.config["stos_password"]
            await page.get_by_placeholder("login").fill(login)
            await page.get_by_placeholder("password").fill(password)
            sumbit = await page.query_selector("[value='Log in']")
            await sumbit.click()
            await page.wait_for_load_state("networkidle")
            link_to_click = self._bot.config["stos_course_name"]
            await page.get_by_text(link_to_click).click()
            await page.wait_for_load_state("networkidle")
            link_to_click = self._bot.config["stos_task_name"]
            await page.get_by_text(link_to_click).click()
            await page.wait_for_load_state("networkidle")
            await page.get_by_text("Submit").click()
            code_snippet = '#include <iostream>\nint main() {\n  std::cout << "Hello, World!";' + \
                '\n  return 0;\n}\n'
            text_field = await page.query_selector("textarea[id=fileedit]")
            await text_field.fill(code_snippet)
            await page.get_by_text("Confirm changes and submit").click()
            start_time = time.time()
            try:
                await page.wait_for_selector("text=Total:", timeout=30*60*1000)
            except TimeoutError:
                await browser.close()
                return -1
            end_time = time.time()
            elapsed_time = end_time - start_time
            await browser.close()
            return elapsed_time

    async def screenshot(self, url: str) -> bytes:
        """ Take a screenshot of a page. """
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()
            if not url.startswith("http") or not url.startswith("https"):
                url = "http://" + url
            try:
                await page.goto(url)
            except Exception as exc:
                await browser.close()
                raise exc
            await page.wait_for_load_state("networkidle")
            image = await page.screenshot()
            await browser.close()
            return image
