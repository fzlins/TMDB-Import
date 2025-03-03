import os
import time, random
from urllib.parse import urlparse, parse_qs
import urllib.request
from dateutil import parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging
from ..processors.image import process_image, TYPE_BACKDROP
from ..common import *
import re

import configparser
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')

def import_spisode(tmdb_id, season_number, language):
    currentData = {}
    importData = read_csv("import.csv")

    if language == "":
        print("Missing language parameter.")
        return 

    driver = ini_webdriver(headless=False, save_user_profile=True, images=True)

    driver.get("https://www.themoviedb.org/login")
    
    if len(driver.find_elements(By.CSS_SELECTOR, value="li[class='user']")) == 0:
        # login
        try:
            
            username = driver.find_element(By.ID, value="username")
            password = driver.find_element(By.ID, value="password")
            tmdb_username = config.get("DEFAULT","tmdb_username", fallback="").strip()
            tmdb_password = config.get("DEFAULT","tmdb_password", fallback="").strip()
            if tmdb_username != "" and tmdb_password != "":
                # automatic login
                username.send_keys(tmdb_username)
                password.send_keys(tmdb_password)

                driver.find_element(By.ID, value="login_button").click()
            else:
                # manual login
                WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.CSS_SELECTOR, value="li[class='user']"))
        except Exception as err:
            logging.error("Falied to login to TMDB", exc_info= err)
            exit()

    # Get season data from tmdb
    driver.get(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/edit?active_nav_item=episodes&language={language}")

    try:
        WebDriverWait(driver, timeout=1).until(lambda d: d.find_element(By.CSS_SELECTOR, value="button[class='k-button k-primary pad_top background_color light_blue translate']")).click()
    except:
        pass

    try:
        # There are no episodes added to this season.
        WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME, value="k-grid-norecords"))
    except:
        WebDriverWait(driver, timeout=30).until(
            lambda d: d.find_element(By.CLASS_NAME, value="k-master-row"))
        for k_master_row in driver.find_elements(By.CLASS_NAME, value="k-master-row"):
            all_columns = k_master_row.find_elements(By.TAG_NAME, "td")
            episode_number = re.sub("[^\d\.]", "", all_columns[0].text) 
            currentData[episode_number] = {}
            currentData[episode_number]["name"] = all_columns[1].text.strip()
            currentData[episode_number]["overview"] = all_columns[2].text.strip()
            currentData[episode_number]["air_date"] = all_columns[3].text.strip()
            currentData[episode_number]["runtime"] = all_columns[4].text.strip()

    # S1E1
    temp = {}
    for episodeNumber in importData:
        numbers = re.findall(r'\d+', episodeNumber)
        if len(numbers) == 2:
            if int(numbers[0]) == int(season_number):
                temp[numbers[1]] = importData[episodeNumber]

    if len(temp) > 0:
        importData = temp

    createList = {}
    updateList = {}
    # Diff
    airDateOverwrite = None
    overviewOverwrite = None
    for episodeNumber in importData:
        if (currentData.__contains__(episodeNumber)):
            # generate update list
            updateEpisode = False
            updateEpisodeData = {}
            if importData[episodeNumber].__contains__("air_date") and len(importData[episodeNumber]["air_date"]) > 0:
                if currentData[episodeNumber]["air_date"].lower() == importData[episodeNumber]["air_date"].lower():
                    pass
                if currentData[episodeNumber]["air_date"].lower() == '' or currentData[episodeNumber]["air_date"].lower() == 'null' or importData[episodeNumber]["air_date"].lower() == 'null' or parser.parse(importData[episodeNumber]["air_date"]) != parser.parse(currentData[episodeNumber]["air_date"]):
                    if (airDateOverwrite):
                        updateEpisodeData["air_date"] = importData[episodeNumber]["air_date"]
                        updateEpisode = True
                    elif airDateOverwrite is None:
                        choice = input("Episode air time does not match, enter 'w' to overwrite it, enter 'y' to always overwrite next time and enter 'n' to always skip overwriting next time. Others will be skipped:")
                        key = choice.strip().lower()
                        if key == "n":
                            airDateOverwrite = False
                        if key == "y":
                            airDateOverwrite = True
                            updateEpisodeData["air_date"] = importData[episodeNumber]["air_date"]
                            updateEpisode = True
                        elif key == "o":
                            updateEpisodeData["air_date"] = importData[episodeNumber]["air_date"]
                            updateEpisode = True

            if importData[episodeNumber].__contains__("name") and len(importData[episodeNumber]["name"]) > 0 and importData[episodeNumber]["name"] != currentData[episodeNumber]["name"]:
                updateEpisodeData["name"] = importData[episodeNumber]["name"]
                updateEpisode = True

            if importData[episodeNumber].__contains__("overview") and len(importData[episodeNumber]["overview"]) > 0:
                if len(importData[episodeNumber]["overview"]) < len(currentData[episodeNumber]["overview"]) + 2:
                    if (overviewOverwrite):
                        updateEpisodeData["overview"] = importData[episodeNumber]["overview"]
                        updateEpisode = True
                    elif overviewOverwrite is None:
                        choice = input("Episode overview is short, enter 'w' to overwrite it, enter 'y' to always overwrite next time and enter 'n' to always skip overwriting next time. Others will be skipped:")
                        key = choice.strip().lower()
                        if key == "n":
                            overviewOverwrite = False
                        elif key == "y":
                            overviewOverwrite = True
                            updateEpisodeData["overview"] = importData[episodeNumber]["overview"]
                            updateEpisode = True
                        elif key == "o":
                            updateEpisodeData["overview"] = importData[episodeNumber]["overview"]
                            updateEpisode = True
                else:
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
            WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class='k-button k-button-icontext k-primary k-grid-update']")))
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.CSS_SELECTOR, value="button[class*='k-button'][class*='k-grid-add']").click()
            episoideID = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.ID, value="episode_number_numeric_text_box_field").get_attribute("value"))
            time.sleep(random.uniform(1, 2))
            if (int(episoideID) != int(episoideNumber)):
                episodeNumberField = driver.find_element(By.CSS_SELECTOR, value="input[role='spinbutton']")
                episodeNumberField.send_keys(Keys.CONTROL + "a")
                actions = ActionChains(driver)
                actions.send_keys(episoideNumber)
                actions.perform()

            episoideName = driver.find_element(By.ID, value=f"{language}_name_text_input_field")
            if (createList[episoideNumber].__contains__("name") and len(createList[episoideNumber]['name']) > 0):
                episoideName.send_keys(createList[episoideNumber]['name'])

            overview = driver.find_element(By.ID, value=f"{language}_overview_text_box_field")
            if (createList[episoideNumber].__contains__("overview") and len(createList[episoideNumber]['overview']) > 0):
                overview.send_keys(importData[episoideNumber]['overview'])

            runtime = driver.find_element(By.ID, value=f"{language}_runtime_text_input_field")
            if (createList[episoideNumber].__contains__("runtime") and len(createList[episoideNumber]['runtime']) > 0):
                runtime.send_keys(importData[episoideNumber]['runtime'])

            if (createList[episoideNumber].__contains__("air_date") and len(createList[episoideNumber]['air_date']) > 0):
                airdate = driver.find_element(By.ID, value="air_date_date_picker_field")
                airdate.clear()
                if createList[episoideNumber]['air_date'].lower() != "null":
                    airdate.send_keys(createList[episoideNumber]['air_date'])

            driver.find_element(By.CSS_SELECTOR, value="button[ref-update-button]").click()

    # update episoides
    for episoideNumber in updateList:
        driver.get(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/episode/{episoideNumber}/edit?active_nav_item=primary_facts&language={language}")

        save_submit = False
        # update name
        if updateList[episoideNumber].__contains__("name"):
            nameInputID = f"{language}_name".replace('-', '_')
            nameInput = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.ID, value=nameInputID))
            if nameInput.get_attribute("disabled") != "true":
                nameInput.clear()
                if updateList[episoideNumber]["name"] != "null":
                    nameInput.send_keys(updateList[episoideNumber]["name"])
                    save_submit = True

        # update overview
        if updateList[episoideNumber].__contains__("overview"):
            overviewInputID = f"{language}_overview".replace('-', '_')
            overviewInput = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.ID, value=overviewInputID))
            if overviewInput.get_attribute("disabled") != "true":
                overviewInput.clear()
                overviewInput.send_keys(updateList[episoideNumber]["overview"])
                save_submit = True

        # update runtime
        if updateList[episoideNumber].__contains__("runtime"):
            runtimeInput = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.ID, value="runtime"))
            if runtimeInput.get_attribute("disabled") != "true":
                runtimeInput.clear()
                runtimeInput.send_keys(updateList[episoideNumber]["runtime"])
                save_submit = True

        # Update air date
        if updateList[episoideNumber].__contains__("air_date"):
            airDateField = WebDriverWait(driver, timeout=30).until(lambda d: d.find_element(By.ID, value="air_date"))
            if airDateField.get_attribute("disabled") != "true":
                airDateField.clear()
                if updateList[episoideNumber]["air_date"].lower() != "null":
                    airDateField.send_keys(updateList[episoideNumber]["air_date"])
                save_submit = True

        if save_submit:
            driver.find_element(By.ID, value="submit").click()
            time.sleep(random.uniform(1, 2))

    # Processing backdrop images
    image_folder = os.path.join(os.getcwd(), "Image")
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    else:
        for imageName in os.listdir(image_folder):
            imagePath = os.path.join(image_folder, imageName)
            os.remove(imagePath)

    backdrop_forced_upload = config.getboolean("DEFAULT","backdrop_forced_upload", fallback=False)
    if not backdrop_forced_upload:
        driver.get(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}")
        time.sleep(3)
        for episoideNumber in importData:
            if (importData[episoideNumber].__contains__("backdrop") and len(importData[episoideNumber]['backdrop']) > 0):
                css_selector = f"div[class='image'] a[episode='{episoideNumber}'][season='{season_number}'] img"
                if len(driver.find_elements(By.CSS_SELECTOR, value=css_selector)) > 0:
                    importData[episoideNumber]['backdrop'] = ""

    for episoideNumber in importData:
        if (importData[episoideNumber].__contains__("backdrop") and len(importData[episoideNumber]['backdrop']) > 0):
            try:
                # download backdrop
                urlData = urlparse(importData[episoideNumber]['backdrop'])
                fileName = f"{tmdb_id}_{season_number}_{episoideNumber}.jpg"
                logging.info(f"{fileName} is downloading...")
                image_path = os.path.join(image_folder, fileName)
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
                        print(new_backdrop_url)
                        urllib.request.urlretrieve(new_backdrop_url, image_path)
                else:
                    urllib.request.urlretrieve(importData[episoideNumber]['backdrop'], image_path)

                # Fit backdrop aspect ratio
                if not process_image(image_path, TYPE_BACKDROP):
                    logging.info("Skip: unable to use fit function to meet TMDB requirments")
                    continue  
                
                # review backdrop
                driver.get(image_path)
                time.sleep(3)

                # upload backdrop
                driver.get(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/episode/{episoideNumber}/images/backdrops")
                if len(driver.find_elements(By.CSS_SELECTOR, value="li[id='no_results']")) != 1 and not backdrop_forced_upload:
                    continue

                driver.find_element(By.CSS_SELECTOR, value="span[class='glyphicons_v2 circle-empty-plus']").click()
                time.sleep(random.uniform(1, 2))
                driver.find_element(By.CSS_SELECTOR, value="input[id='upload_files']").send_keys(image_path)
                WebDriverWait(driver, timeout=30).until(lambda d: "successfully" in d.find_element(By.CSS_SELECTOR, value="span[class='k-file-validation-message']").text)

                # thumbs up upload backdrop
            except Exception as e:
                logging.error(
                    f"Download/upload backdrop error for: {importData[episoideNumber]['backdrop']}.", exc_info=e)

    driver.quit()
    return
