from PIL import Image, ImageOps
import logging
import bordercrop

TYPE_BACKDROP = "backdrop"
TYPE_POSTER = "poster"

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
            logging.info(f"Original image size: {image.size[0]} * {image.size[1]}")
            logging.info(f"Cropped black border and new image size: {tempImage.size[0]} * {tempImage.size[1]}")
            image = tempImage
            image.save(image_path, format="JPEG", quality=92)
    except Exception as err:
        logging.error(err)
    image.close()

def fit_aspect_ratio(image_path, type):   
    image = Image.open(image_path)
    image_widith, image_heigh = image.size
    logging.debug(f"Image size: {image_widith} * {image_heigh}")
    if type == TYPE_BACKDROP:
        aspectRatio = round(image_widith/image_heigh, 2)
        if aspectRatio == 1.78 and (image_widith >= 1280 and image_heigh >= 720) and (image_widith <= 3840 and image_heigh <= 2106):
            # valid image siez
            pass
        elif (aspectRatio >= 1.6 or aspectRatio <= 1.9) and (image_widith >= 960 and image_heigh >= 540):
            # resize image to fit valid size
            re_size = (1280, 720)
            # (1280, 720)*1.35
            if image_widith < 1280 or image_heigh < 720:
                pass
            elif image_widith > 3840 and image_heigh > 2160:
                re_size = (2880, 1620)
            else:
                if aspectRatio < 1.78:
                    re_size = (round(image_heigh * 1.78), image_heigh)
                else:
                    re_size = (image_widith, round(image_widith / 1.78))

            logging.info(f"Resize backdrop to {re_size[0]}*{re_size[1]}")
            image = ImageOps.fit(image=image, size=re_size, method=Image.Resampling.LANCZOS, bleed=0.0, centering=(0.5, 0.5))
            image.save(image_path, format="JPEG", quality=85)
        else:
            logging.info("Skip: unable to use fit function to meet TMDB requirments")
            return False
    elif type == TYPE_POSTER:
        aspectRatio = round(image_heigh/image_widith, 2)
        if aspectRatio == 1.50 and (image_widith >= 500 and image_heigh >= 750) and (image_widith <= 2000 and image_heigh <= 3000):
            # valid image siez
            pass
        elif (aspectRatio >= 1.40 or aspectRatio <= 1.60) and (image_widith >= 400 and image_heigh >= 600):
            re_size = (500, 750)
            if image_widith < 500 or image_heigh < 750:
                pass
            elif image_widith > 2000 and image_heigh > 3000:
                re_size = (2000, 3000)
            else:
                if aspectRatio < 1.5:
                    re_size = (round(image_heigh/1.5), image_heigh)
                else:
                    re_size = (image_widith, round(image_widith * 1.5))
            logging.info(f"Resize poster to {re_size[0]}*{re_size[1]}")
            image = ImageOps.fit(image=image, size=re_size, method=Image.Resampling.LANCZOS, bleed=0.0, centering=(0.5, 0.5))
            image.save(image_path, format="JPEG", quality=85)
        else:
            logging.info("Skip: unable to use fit function to meet TMDB requirments")
            return False

    image.close()
    return True

def process_image(image_path, type):
    # Convert other format to jpg
    convert_to_jpg(image_path)
    
    # Crop black border
    crop_black_border(image_path)
    
    # Fit backdrop aspect ratio
    return fit_aspect_ratio(image_path, type)

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