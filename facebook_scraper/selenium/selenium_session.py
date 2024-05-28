"""
Imitate requests_html.HTMLSession with selinium
"""
from requests import HTTPError
from requests_html import HTMLResponse, HTML
from selenium import webdriver
from selenium.webdriver.common.by import By

from facebook_scraper.selenium.extension import proxies, http_status_extension


class SeleniumSession:
    def __init__(self, proxy_username, proxy_password, endpoint, proxy_port):
        chrome_options = webdriver.ChromeOptions()
        proxies_extension = proxies(proxy_username, proxy_password, endpoint, proxy_port)
        chrome_options.add_extension(proxies_extension)
        http_status_ext = http_status_extension()
        chrome_options.add_extension(http_status_ext)
        # chrome_options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=chrome_options)

    def get(self, url, **kwargs):
        # assert "proxies" in kwargs, "Only proxies are supported"
        self.driver.get(url)

        return HTMLResponse(session=self)

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
    def __init__(self, session: SeleniumSession=None):
        self.text = session.driver.page_source
        self.session = session
        self.url = session.driver.current_url
        self._html = None

    @property
    def html(self):
        if self._html is None:
            self._html = HTML(url=self.url, html=self.text)
        return self._html

    def raise_for_status(self):
        http_status_code = int(self.session.driver.get_cookie("status-code")['value'])

        if http_status_code != 200:
            http_error_msg = ''
            reason = self.session.driver.find_element(By.cssSelector("#mainContent~h1")).isDisplayed();

            if isinstance(reason, bytes):
                # We attempt to decode utf-8 first because some servers
                # choose to localize their reason strings. If the string
                # isn't utf-8, we fall back to iso-8859-1 for all other
                # encodings. (See PR #3538)
                try:
                    reason = reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = reason.decode('iso-8859-1')

            if 400 <= http_status_code < 500:
                http_error_msg = u'%s Client Error: %s for url: %s' % (http_status_code, reason, self.url)

            elif 500 <= http_status_code < 600:
                http_error_msg = u'%s Server Error: %s for url: %s' % (http_status_code, reason, self.url)

            if http_error_msg:
                raise HTTPError(http_error_msg, response=self)

