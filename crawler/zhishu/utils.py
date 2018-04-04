# coding=utf-8
#


"""
aso100爬虫相关的功能函数集合
"""

import json
import time
import random

from datetime import datetime
from datetime import timedelta

from selenium import webdriver


def get_browser():
    """
        获取浏览器实例

        :return: browser
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": "/tmp/aso/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})

    browser = webdriver.Chrome(chrome_options=options)

    return browser

