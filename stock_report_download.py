import os
import time
import shutil
import conf
import pprint

from selenium import webdriver

def stock_report_download():
    """
    Downloads the stock report from the s2.equipweb.biz using selenium
    """

    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')  # Optional argument, if not specified will search path.
    driver.get(conf.login_url)
    time.sleep(4)

    username = driver.find_element_by_id("UserName")
    password = driver.find_element_by_id("Password")

    username.send_keys(conf.user_name)
    time.sleep(1)

    password.send_keys(conf.password)
    time.sleep(1)

    driver.find_element_by_id("submitBtn").click()
    time.sleep(3)

    driver.get(conf.stock_with_price_url)
    time.sleep(2)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_LinkButton2").click()

    filename = max([conf.download_directory + "/" + f for f in os.listdir(conf.download_directory)], key=os.path.getctime)
    shutil.move(filename,os.path.join(conf.download_directory, conf.downloaded_latest_file_name))

    time.sleep(1)
    driver.find_element_by_id("ctl00_logoutBtn").click()
    time.sleep(3)

    driver.quit()

if __name__ == "__main__":
    stock_report_download()

