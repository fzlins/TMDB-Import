# coding= utf-8
tmdb_username = "username"
tmdb_password = "password"
tmdbID = 116644
seasonID = 1
donwloadBacdrop = False
uploadBackdrop = False

backdropUrl = ""

# "zh-CN", "ja-JP", "en-US"
language = "ja-JP"

currentData = {}
importData = {}

import csv
with open('import.csv', newline='', encoding='utf-8') as csvfile:
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
from urllib.parse import urlparse

options = webdriver.EdgeOptions()

# load user data
options.add_argument("user-data-dir=" + os.getcwd() + "\\Selenium") 
driver = webdriver.Edge(options=options)

# login
try:
    driver.get("https://www.themoviedb.org/login")
    username = driver.find_element_by_id("username")
    password = driver.find_element_by_id("password")

    username.send_keys(tmdb_username)
    password.send_keys(tmdb_password)

    driver.find_element_by_id("login_button").click()
except:
    print('User is logged')

# Get season data from tmdb
driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/edit?active_nav_item=episodes&language={language}")

try:
    WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_class_name("k-grid-norecords")) # There are no episodes added to this season.
except:
    WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_class_name("k-master-row"))
    for k_master_row in driver.find_elements_by_class_name("k-master-row"):
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

        if importData[episodeNumber].__contains__("air_date") > 0 and (currentData[episodeNumber]["air_date"].lower() == 'null' or parser.parse(importData[episodeNumber]["air_date"]) != parser.parse(currentData[episodeNumber]["air_date"])):
            updateEpisodeData["air_date"] = importData[episodeNumber]["air_date"]
            updateEpisode = True

        if importData[episodeNumber].__contains__("name") and importData[episodeNumber]["name"] != currentData[episodeNumber]["name"]:
            updateEpisodeData["name"] = importData[episodeNumber]["name"]
            updateEpisode = True

        if importData[episodeNumber].__contains__("overview") and len(currentData[episodeNumber]["overview"]) == 0:
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
        driver.find_element_by_css_selector("a[class='k-button k-button-icontext k-grid-add']").click()
        episoideID = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_id("episode_number_numeric_text_box_field").get_attribute("value"))

        if (int(episoideID) != int(episoideNumber)):
            episodeNumberField = driver.find_element_by_id("episode_number_numeric_text_box_field")
            episodeNumberField.clear()
            episodeNumberField.send_keys(episoideNumber)

        episoideName = driver.find_element_by_id(f"{language}_name_text_input_field")
        if (createList[episoideNumber].__contains__("name") and len(createList[episoideNumber]['name']) > 0) :       
            episoideName.send_keys(createList[episoideNumber]['name'])

        overview = driver.find_element_by_id(f"{language}_overview_text_box_field")
        if (createList[episoideNumber].__contains__("overview") and len(createList[episoideNumber]['overview']) > 0) :
            overview.send_keys(importData[episoideNumber]['overview'])

        runtime = driver.find_element_by_id(f"{language}_runtime_text_input_field")
        if (createList[episoideNumber].__contains__("runtime") and len(createList[episoideNumber]['runtime']) > 0) :
            runtime.send_keys(importData[episoideNumber]['runtime'])

        if (createList[episoideNumber].__contains__("air_date") and len(createList[episoideNumber]['air_date']) > 0) :
            airdate = driver.find_element_by_id("air_date_date_picker_field")
            dateFormate = createList[episoideNumber]['air_date'].split('.')
            if (len(dateFormate) == 3):
                createList[episoideNumber]['air_date'] = dateFormate[2] + "/" + dateFormate[1] + "/" + dateFormate[0]
            airdate.clear()
            if createList[episoideNumber]['air_date'].lower() != "null":
                airdate.send_keys(createList[episoideNumber]['air_date'])

        driver.find_element_by_css_selector("a[class='k-button k-button-icontext k-primary k-grid-update']").click()

# update episoides
for episoideNumber in updateList:
    driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/episode/{episoideNumber}/edit?active_nav_item=primary_facts&language={language}")
    
    # update name
    if updateList[episoideNumber].__contains__("name"):
        nameInputID = f"{language}_name".replace('-','_')
        nameInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_id(nameInputID))
        nameInput.clear()
        if updateList[episoideNumber]["name"] != "null":
            nameInput.send_keys(updateList[episoideNumber]["name"])

    # update overview
    if updateList[episoideNumber].__contains__("overview"):
        overviewInputID = f"{language}_overview".replace('-','_')
        overviewInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_id(overviewInputID))
        overviewInput.clear()
        overviewInput.send_keys(updateList[episoideNumber]["overview"])

    # update runtime
    if updateList[episoideNumber].__contains__("runtime"):
        runtimeInput = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_id("runtime"))
        runtimeInput.clear()
        runtimeInput.send_keys(updateList[episoideNumber]["runtime"])   

    # Update air date
    if updateList[episoideNumber].__contains__("air_date"):
        airDateField = WebDriverWait(driver, timeout=60).until(lambda d: d.find_element_by_id("air_date"))
        airDateField.clear()
        if updateList[episoideNumber]["air_date"].lower() != "null":
            airDateField.send_keys(updateList[episoideNumber]["air_date"])

    driver.find_element_by_id("submit").click()
    time.sleep(1)

# Processing backdrop images
imageFolder = "Image/"
if not os.path.exists(imageFolder):
    os.makedirs(imageFolder)
else:
    for imageName in os.listdir(imageFolder):
        imagePath = os.path.join(imageFolder, imageName)
        os.remove(imagePath)
if (donwloadBacdrop):
    for episoideNumber in importData:
        if (importData[episoideNumber].__contains__("backdrop")):
            # download backdrop
            urlData = urlparse(importData[episoideNumber]['backdrop'])
            fileName = urlData.path.rsplit('/', 1)[-1]
            urllib.request.urlretrieve(importData[episoideNumber]['backdrop'], imageFolder + fileName)
            
            # upload backdrop
            if (uploadBackdrop):
                driver.get(f"https://www.themoviedb.org/tv/{tmdbID}/season/{seasonID}/episode/{episoideNumber}/images/backdrops")
                driver.find_element_by_css_selector("span[class='glyphicons_v2 circle-empty-plus']").click()
                fileFullName = os.path.dirname(os.path.realpath(__file__)) + "\Image\\" + fileName
                time.sleep(1)
                driver.find_element_by_css_selector("input[id='upload_files']").send_keys(fileFullName)
                time.sleep(10)

driver.quit()