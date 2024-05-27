"""
Imitate requests_html.HTMLSession with selinium
"""
from requests_html import HTMLResponse, HTML
from selenium import webdriver

from facebook_scraper.selenium.extension import proxies


class SeleniumSession:
    def __init__(self, proxy_username, proxy_password, endpoint, proxy_port):
        chrome_options = webdriver.ChromeOptions()
        proxies_extension = proxies(proxy_username, proxy_password, endpoint, proxy_port)
        chrome_options.add_extension(proxies_extension)
        # chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=chrome_options)

    def get(self, url, **kwargs):
        # assert "proxies" in kwargs, "Only proxies are supported"
        self.driver.get(url)

        return HTMLResponse(page_source=self.driver.page_source)

    @property
    def content(self):
        return self.driver.page_source

    @property
    def encoding(self):
        return "utf-8"

    def post(self, url, data, **kwargs):
        raise NotImplementedError("post not implemented")

    def close(self):
        self.driver.close()
        self.driver.quit()

    @property
    def headers(self):
        #return self.driver.execute_script("return navigator.webdriver")
        return {}   # Dummy headers

    @property
    def cookies(self):
        return CookieDict(self.driver)


class CookieDict:
    def __init__(self, driver):
        self.driver = driver

    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return self.driver.get_cookie(key)

    def __setitem__(self, key, value):
        self.driver.add_cookie({key: value})


class HTMLResponse:
    def __init__(self, page_source=None, session: SeleniumSession=None):
        self._html = HTML(html=page_source)
        self.session = session

    @property
    def html(self):
        return self._html

    def raise_for_status(self):
        self.session.driver.h