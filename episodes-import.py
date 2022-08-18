# coding= utf-8-sig
import logging, re
logging.basicConfig(filename='episodes-import.log', level=logging.INFO)

tmdb_username = "username"
tmdb_password = "password"
tmdbID = 200940
seasonID = 1
donwloadBacdrop = True
uploadBackdrop = True

backdropUrl = ""

# "zh-CN", "ja-JP", "en-US"
language = "zh-CN"

currentData = {}
importData = {}

import csv
with open('import.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        importData[row['episode_number'].strip()] = row 
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, os
from dateutil import parser
import urllib.request
from urllib.parse import urlparse, parse_qs

options = webdriver.EdgeOptions()

# load user data
options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 
options.add_argument('--disable-gpu')
options.add_argument('log-level=3')
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})

driver = webdriver.Edge(options=options)

# login
try:
    driver.get("https://www.themoviedb.org/login")
    username = driver.find_element(By.ID, value="username")
    password = driver.find_element(By.ID, value="password")

    username.send_keys(tmdb_username)
    password.send_keys(tmdb_password)

    driver.find_element(By.ID, value="login_button").click()
except:
    print('User is logged')

# Get season data from tmdb
driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/edit?active_nav_item=episodes&language={language}")

try:
    WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, value="k-grid-norecords")) # There are no episodes added to this season.
except:
    WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.CLASS_NAME, value="k-master-row"))
    for k_master_row in driver.find_elements(By.CLASS_NAME, value="k-master-row"):
        all_columns = k_master_row.find_elements(By.TAG_NAME,"td")
        episode_number = all_columns[0].text.strip()
        currentData[episode_number] = {}
        currentData[episode_number]["name"] = all_columns[1].text.strip()
        currentData[episode_number]["overview"] = all_columns[2].text.strip()
        currentData[episode_number]["air_date"] = all_columns[3].text.strip()
        currentData[episode_number]["runtime"] = all_columns[4].text.strip()

createList = {}
updateList = {}
# Diff
for episodeNumber in importData:
    if (currentData.__contains__(episodeNumber)):
        # generate update list
        updateEpisode = False
        updateEpisodeData = {}
        if importData[episodeNumber].__contains__("air_date") and len(importData[episodeNumber]["air_date"]) > 0: 
            if (currentData[episodeNumber]["air_date"].lower() == 'null' and importData[episodeNumber]["air_date"].lower() != 'null') or parser.parse(importData[episodeNumber]["air_date"]) != parser.parse(currentData[episodeNumber]["air_date"]):
                updateEpisodeData["air_date"] = importData[episodeNumber]["air_date"]
                updateEpisode = True

        if importData[episodeNumber].__contains__("name") and len(importData[episodeNumber]["name"]) > 0 and importData[episodeNumber]["name"] != currentData[episodeNumber]["name"]:
            updateEpisodeData["name"] = importData[episodeNumber]["name"]
            updateEpisode = True

        if importData[episodeNumber].__contains__("overview") and len(importData[episodeNumber]["overview"]) > len(currentData[episodeNumber]["overview"]) + 50:
            updateEpisodeData["overview"] = importData[episodeNumber]["overview"]
            updateEpisode = True
        
        if importData[episodeNumber].__contains__("runtime"):
            importData[episodeNumber]["runtime"] = ''.join(filter(str.isdigit, importData[episodeNumber]["runtime"]))
            if len(importData[episodeNumber]["runtime"]) > 0 and importData[episodeNumber]["runtime"] != currentData[episodeNumber]["runtime"]:
                updateEpisodeData["runtime"] = importData[episodeNumber]["runtime"]
                updateEpisode = True

        if updateEpisode:
            updateList[episodeNumber] = updateEpisodeData
    else:
        # generate create list
        createList[episodeNumber] = importData[episodeNumber]

# create episodes
if len(createList) > 0:
    for episoideNumber in createList:
        WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class='k-button k-button-icontext k-primary k-grid-update']")))
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, value="a[class='k-button k-button-icontext k-grid-add']").click()
        episoideID = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value="episode_number_numeric_text_box_field").get_attribute("value"))

        if (int(episoideID) != int(episoideNumber)):
            episodeNumberField = driver.find_element(By.ID, value="episode_number_numeric_text_box_field")
            episodeNumberField.clear()
            episodeNumberField.send_keys(episoideNumber)

        episoideName = driver.find_element(By.ID, value=f"{language}_name_text_input_field")
        if (createList[episoideNumber].__contains__("name") and len(createList[episoideNumber]['name']) > 0) :       
            episoideName.send_keys(createList[episoideNumber]['name'])

        overview = driver.find_element(By.ID, value=f"{language}_overview_text_box_field")
        if (createList[episoideNumber].__contains__("overview") and len(createList[episoideNumber]['overview']) > 0) :
            overview.send_keys(importData[episoideNumber]['overview'])

        runtime = driver.find_element(By.ID, value=f"{language}_runtime_text_input_field")
        if (createList[episoideNumber].__contains__("runtime") and len(createList[episoideNumber]['runtime']) > 0) :
            runtime.send_keys(importData[episoideNumber]['runtime'])

        if (createList[episoideNumber].__contains__("air_date") and len(createList[episoideNumber]['air_date']) > 0) :
            airdate = driver.find_element(By.ID, value="air_date_date_picker_field")
            airdate.clear()
            if createList[episoideNumber]['air_date'].lower() != "null":
                airdate.send_keys(createList[episoideNumber]['air_date'])

        driver.find_element(By.CSS_SELECTOR, value="a[class='k-button k-button-icontext k-primary k-grid-update']").click()

# update episoides
for episoideNumber in updateList:
    driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/episode/{episoideNumber}/edit?active_nav_item=primary_facts&language={language}")
    
    # update name
    if updateList[episoideNumber].__contains__("name"):
        nameInputID = f"{language}_name".replace('-','_')
        nameInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value=nameInputID))
        nameInput.clear()
        if updateList[episoideNumber]["name"] != "null":
            nameInput.send_keys(updateList[episoideNumber]["name"])

    # update overview
    if updateList[episoideNumber].__contains__("overview"):
        overviewInputID = f"{language}_overview".replace('-','_')
        overviewInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value=overviewInputID))
        overviewInput.clear()
        overviewInput.send_keys(updateList[episoideNumber]["overview"])

    # update runtime
    if updateList[episoideNumber].__contains__("runtime"):
        runtimeInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value="runtime"))
        runtimeInput.clear()
        runtimeInput.send_keys(updateList[episoideNumber]["runtime"])   

    # Update air date
    if updateList[episoideNumber].__contains__("air_date"):
        airDateField = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value="air_date"))
        airDateField.clear()
        if updateList[episoideNumber]["air_date"].lower() != "null":
            airDateField.send_keys(updateList[episoideNumber]["air_date"])

    driver.find_element(By.ID, value="submit").click()
    time.sleep(1)

# Processing backdrop images
from PIL import Image, ImageOps

imageFolder = "Image/"
if not os.path.exists(imageFolder):
    os.makedirs(imageFolder)
else:
    for imageName in os.listdir(imageFolder):
        imagePath = os.path.join(imageFolder, imageName)
        os.remove(imagePath)
if (donwloadBacdrop):
    for episoideNumber in importData:
        if (importData[episoideNumber].__contains__("backdrop") and len(importData[episoideNumber]['backdrop']) > 0 ):
            try:
                # download backdrop
                urlData = urlparse(importData[episoideNumber]['backdrop'])
                fileName = urlData.path.rsplit('/', 1)[-1]
                image_path = imageFolder + fileName
                if urlData.query.__contains__('imageWidth') and urlData.query.__contains__('imageHeight'):
                    backdrop_url = importData[episoideNumber]['backdrop'].split('?')[0]
                    new_backdrop_url = backdrop_url.replace("imageWidth", "0").replace("imageHeight", "0")
                    try:
                        urllib.request.urlretrieve(new_backdrop_url, image_path)
                    except:
                        urlQuery = parse_qs(urlData.query)
                        imageWidth = urlQuery["imageWidth"][0]
                        imageHeight = urlQuery["imageHeight"][0]
                        logging.info(f"Download backdrop with 0*0 failed, try to use default pixel: {imageWidth}*{imageHeight}")
                        new_backdrop_url = backdrop_url.replace("imageWidth", imageWidth).replace("imageHeight", imageHeight)
                        urllib.request.urlretrieve(new_backdrop_url, image_path)
                else:
                    urllib.request.urlretrieve(importData[episoideNumber]['backdrop'], image_path)

                image = Image.open(image_path)

                # Convert other format to jpg
                if image.mode != "RGB":
                    logging.info("Convert other format to jpg")
                    image = image.convert("RGB")
                    image.save(image_path, format= "JPEG", quality= 85)

                image_widith, image_heigh = image.size
                logging.info(f"Backdrop size: {image_widith} * {image_heigh}")
                aspectRatio = round(image_widith/image_heigh, 2)
                if aspectRatio == 1.78 and (image_widith >= 1280 and image_heigh >= 720) and (image_widith <= 3840 and image_heigh <= 2106):
                    # valid image siez
                    pass
                elif (aspectRatio >= 1.6 or aspectRatio <= 1.9) and (image_widith >= 960 and image_heigh >= 540):
                    # resize image to fit valid size
                    re_size = (1280, 720)
                    if image_widith < 1728 or image_heigh < 972: # (1280, 720)*1.35
                        re_size = (1280, 720)
                    elif image_widith < 2592 or image_heigh < 1458: # (1920, 1080)*1.35
                        re_size = (1920, 1080)
                    elif image_widith < 3600 or image_heigh < 2025: # (2880, 1620)*1.25
                        re_size = (2880, 1620)
                    logging.info(f"Upscale image to {re_size[0]}*{re_size[1]}")
                    image = ImageOps.fit(image=image, size=re_size, method=Image.Resampling.LANCZOS, bleed=0.0, centering=(0.5, 0.5))
                    image.save(image_path, format= "JPEG", quality= 90)
                else:
                    logging.info("Skip: unable to use fit function to meet TMDB requirments")
                    continue
                image.close()

                # upload backdrop
                if (uploadBackdrop):
                    driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/episode/{episoideNumber}/images/backdrops")
                    driver.find_element(By.CSS_SELECTOR, value="span[class='glyphicons_v2 circle-empty-plus']").click()
                    fileFullName = os.path.dirname(os.path.realpath(__file__)) + "\Image\\" + fileName
                    time.sleep(1)
                    driver.find_element(By.CSS_SELECTOR, value="input[id='upload_files']").send_keys(fileFullName)
                    time.sleep(10)
            except Exception as e:
                logging.error(f"Download/upload backdrop error for: {importData[episoideNumber]['backdrop']}.", exc_info= e)

driver.quit()