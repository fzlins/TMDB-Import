from PIL import Image, ImageOps
import logging
import bordercrop

def convert_to_jpg(image_path):
    image = Image.open(image_path)
    if image.mode != "RGB":
        logging.info(f"Convert {image.mode} to RGB")
        image = image.convert("RGB")
        image.save(image_path, format="JPEG", quality=92)
    elif image.format != "JPEG":
        logging.info(f"Convert {image.format} to JPEG")
        image.save(image_path, format="JPEG", quality=92)
    image.close()

def crop_black_border(image_path):
    try:
        image = Image.open(image_path)         
        tempImage = bordercrop.crop(image_path, 1, round(image.size[1]*0.99), 100)
        if (tempImage.size[0] < image.size[0] or tempImage.size[1] < image.size[1]):
            logging.info(f"Original backdrop size: {image.size[0]} * {image.size[1]}")
            logging.info(f"Cropped backdrop size: {tempImage.size[0]} * {tempImage.size[1]}")
            image = tempImage
            image.save(image_path, format="JPEG", quality=92)
    except Exception as err:
        logging.error(err)
    image.close()

def fit_aspect_ratio(image_path, required_aspect_ratio):   
    image = Image.open(image_path)
    image_widith, image_heigh = image.size
    logging.debug(f"Backdrop size: {image_widith} * {image_heigh}")
    aspectRatio = round(image_widith/image_heigh, 2)
    if required_aspect_ratio == 1.78:
        if aspectRatio == required_aspect_ratio and (image_widith >= 1280 and image_heigh >= 720) and (image_widith <= 3840 and image_heigh <= 2106):
            # valid image siez
            pass
        elif (aspectRatio >= 1.6 or aspectRatio <= 1.9) and (image_widith >= 960 and image_heigh >= 540):
            # resize image to fit valid size
            re_size = (1280, 720)
            # (1280, 720)*1.35
            if image_widith < 1728 or image_heigh < 972:
                re_size = (1280, 720)
            # (1920, 1080)*1.35
            elif image_widith < 2592 or image_heigh < 1458:
                re_size = (1920, 1080)
            # (2880, 1620)*1.25
            elif image_widith < 3600 or image_heigh < 2025:
                re_size = (2880, 1620)
            logging.info(f"Upscale image to {re_size[0]}*{re_size[1]}")
            image = ImageOps.fit(image=image, size=re_size, method=Image.Resampling.LANCZOS, bleed=0.0, centering=(0.5, 0.5))
            image.save(image_path, format="JPEG", quality=85)
        else:
            logging.info("Skip: unable to use fit function to meet TMDB requirments")
            return False                
    image.close()
    return True

def process_backdrop(image_path):
    # Convert other format to jpg
    convert_to_jpg(image_path)
    
    # Crop black border
    crop_black_border(image_path)

    # Fit backdrop aspect ratio
    return fit_aspect_ratio(image_path, 1.78)

'''
from ..common import ini_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import time

# https://www.themoviedb.org/tv/136891/season/1/episode/1/images/backdrops?language=xx
# Not working
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
'''