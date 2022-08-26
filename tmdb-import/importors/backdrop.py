from ..common import ini_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import time

# https://www.themoviedb.org/tv/136891/season/1/episode/1/images/backdrops?language=xx


def backdrop_thumbs_up(url, driver = None):
    if driver==None:
        driver = ini_webdriver(headless=False, save_user_profile=True, images=True)
    
    driver.get(url)
    
    username = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CSS_SELECTOR, value="div[class='avatar'] img")).get_attribute("alt")
    print(username)
    backdrop_id = ""
    for card_compact in WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements(By.CSS_SELECTOR, value="li[class='card compact']")):
        print(backdrop_id)
        if len(card_compact.find_elements(By.LINK_TEXT, value=username)) > 0 and card_compact.get_attribute("id") > backdrop_id:
            backdrop_id = card_compact.get_attribute("id")
            print(backdrop_id)

    if backdrop_id != "":
        action = webdriver.ActionChains(driver)
        element = driver.find_element(By.CSS_SELECTOR, value=f"a[id='{backdrop_id}'][class='thumbs_up']")
        time.sleep(1)
        action.move_to_element(element).click(element)
        print("thumbs_up")     