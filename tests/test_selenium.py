import datetime
import logging
import time

import pytest

import facebook_scraper
from facebook_scraper.selenium.selenium_session import SeleniumSession

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# @pytest.mark.vcr()
class TestGetPosts:
    def test_selenium(self):
        proxy_username = "USERNAME"

        proxy_password = "PASSWORD"
        endpoint = 'PROXY_URL'

        proxy_port = 99999  # YOUR PROXY PORT

        session = SeleniumSession(proxy_username, proxy_password, endpoint, proxy_port)
        facebook_scraper._scraper = facebook_scraper.FacebookScraper(session)

        # facebook_scraper.set_proxy(f"http://{proxy_username}:{proxy_password}@{endpoint}:{proxy_port}/")

        # group_id = 1152139018170361     # working
        group_id = 441654752934426     # problematic
        # group_id = 170918513059147      # anime
        max_past_limit = 2
        max_days_back = 2
        post_iter = facebook_scraper.get_posts(group=group_id, options={"allow_extra_requests": False},
                                               #max_past_limit=max_past_limit,
                                               #latest_date=datetime.datetime.now() - datetime.timedelta(
                                               #    days=max_days_back),
                                               )
        try:
            post = next(post_iter)
            print(post)
        except StopIteration:
            pass
        time.sleep(1000)
        # time.sleep(100)
        for i in range(4):
            post = next(post_iter)
            print(post)
            assert post


if __name__ == "__main__":
    TestGetPosts().test_selenium()
