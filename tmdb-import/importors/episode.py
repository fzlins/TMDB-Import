import os
import time, random
from urllib.parse import urlparse, parse_qs
import urllib.request
from dateutil import parser
import logging
from ..processors.image import process_image, TYPE_BACKDROP
from ..common import *
import re

import configparser
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')

def import_spisode(tmdb_id, season_number, language, csv_filename="import.csv"):
    currentData = {}
    importData = read_csv(csv_filename)

    if language == "":
        print("Missing language parameter.")
        return 

    page = None
    try:
        page = ini_playwright_page(save_user_profile=True, images=True)
    except (PlaywrightBrowserError, PlaywrightInstallationError) as e:
        logging.error(f"Failed to initialize browser for episode import: {e}")
        print(f"Error: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error initializing browser: {e}")
        print(f"Unexpected error: {e}")
        return

    try:
        # Navigate to TMDB login with error handling
        try:
            page.goto("https://www.themoviedb.org/login", timeout=30000)
        except Exception as e:
            raise PlaywrightError(f"Failed to navigate to TMDB login page: {e}") from e
        
        if len(page.locator("li[class='user']").all()) == 0:
            # login
            try:
                
                username = page.locator("#username")
                password = page.locator("#password")
                tmdb_username = config.get("DEFAULT","tmdb_username", fallback="").strip()
                tmdb_password = config.get("DEFAULT","tmdb_password", fallback="").strip()
                if tmdb_username != "" and tmdb_password != "":
                    # automatic login
                    username.fill(tmdb_username)
                    password.fill(tmdb_password)

                    page.locator("#login_button").click()
                    # Wait for login to complete
                    page.wait_for_selector("li[class='user']", timeout=30000)
                else:
                    # manual login
                    page.wait_for_selector("li[class='user']", timeout=30000)
            except Exception as err:
                logging.error("Falied to login to TMDB", exc_info= err)
                exit()

        # Get season data from tmdb
        page.goto(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/edit?active_nav_item=episodes&language={language}")

        try:
            page.wait_for_selector("button[class='k-button k-primary pad_top background_color light_blue translate']", timeout=1000)
            page.locator("button[class='k-button k-primary pad_top background_color light_blue translate']").click()
        except:
            pass

        try:
            # There are no episodes added to this season.
            page.wait_for_selector(".k-grid-norecords", timeout=3000)
        except:
            page.wait_for_selector(".k-master-row", timeout=30000)
            for k_master_row in page.locator(".k-master-row").all():
                all_columns = k_master_row.locator("td").all()
                episode_number = re.sub(r"[^\d\.]", "", all_columns[0].text_content()) 
                currentData[episode_number] = {}
                currentData[episode_number]["name"] = all_columns[1].text_content().strip()
                currentData[episode_number]["overview"] = all_columns[2].text_content().strip()
                currentData[episode_number]["air_date"] = all_columns[3].text_content().strip()
                currentData[episode_number]["runtime"] = all_columns[4].text_content().strip()

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
                # Wait for update button to disappear
                try:
                    page.wait_for_selector("button[class='k-button k-button-icontext k-primary k-grid-update']", state="detached", timeout=60000)
                except:
                    pass
                time.sleep(random.uniform(1, 2))
                page.locator("button[class*='k-button'][class*='k-grid-add']").click()
                time.sleep(random.uniform(1, 2))
                # Wait for episode number field and get its value
                episoideID = page.locator("#episode_number_numeric_text_box_field").get_attribute("aria-valuenow", timeout=60000)
                time.sleep(random.uniform(1, 2))
                
                if (int(episoideID) != int(episoideNumber)):
                    episodeNumberField = page.locator("input[role='spinbutton']")
                    episodeNumberField.press("Control+a")
                    episodeNumberField.type(str(episoideNumber))

                episoideName = page.locator(f"#{language}_name_text_input_field")
                if (createList[episoideNumber].__contains__("name") and len(createList[episoideNumber]['name']) > 0):
                    episoideName.fill(createList[episoideNumber]['name'])

                overview = page.locator(f"#{language}_overview_text_box_field")
                if (createList[episoideNumber].__contains__("overview") and len(createList[episoideNumber]['overview']) > 0):
                    overview.fill(importData[episoideNumber]['overview'])

                runtime = page.locator(f"#{language}_runtime_text_input_field")
                if (createList[episoideNumber].__contains__("runtime") and len(createList[episoideNumber]['runtime']) > 0):
                    runtime.fill(importData[episoideNumber]['runtime'])

                if (createList[episoideNumber].__contains__("air_date") and len(createList[episoideNumber]['air_date']) > 0):
                    airdate = page.locator("#air_date_date_picker_field")
                    airdate.clear()
                    if createList[episoideNumber]['air_date'].lower() != "null":
                        airdate.fill(createList[episoideNumber]['air_date'])

                page.locator("button[ref-update-button]").click()

        # update episoides
        for episoideNumber in updateList:
            page.goto(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/episode/{episoideNumber}/edit?active_nav_item=primary_facts&language={language}")

            save_submit = False
            # update name
            if updateList[episoideNumber].__contains__("name"):
                nameInputID = f"{language}_name".replace('-', '_')
                page.wait_for_selector(f"#{nameInputID}", timeout=30000)
                nameInput = page.locator(f"#{nameInputID}")
                if nameInput.get_attribute("disabled") != "true":
                    nameInput.clear()
                    if updateList[episoideNumber]["name"] != "null":
                        nameInput.fill(updateList[episoideNumber]["name"])
                        save_submit = True

            # update overview
            if updateList[episoideNumber].__contains__("overview"):
                overviewInputID = f"{language}_overview".replace('-', '_')
                page.wait_for_selector(f"#{overviewInputID}", timeout=30000)
                overviewInput = page.locator(f"#{overviewInputID}")
                if overviewInput.get_attribute("disabled") != "true":
                    overviewInput.clear()
                    overviewInput.fill(updateList[episoideNumber]["overview"])
                    save_submit = True

            # update runtime
            if updateList[episoideNumber].__contains__("runtime"):
                page.wait_for_selector("#runtime", timeout=30000)
                runtimeInput = page.locator("#runtime")
                if runtimeInput.get_attribute("disabled") != "true":
                    runtimeInput.clear()
                    runtimeInput.fill(updateList[episoideNumber]["runtime"])
                    save_submit = True

            # Update air date
            if updateList[episoideNumber].__contains__("air_date"):
                page.wait_for_selector("#air_date", timeout=30000)
                airDateField = page.locator("#air_date")
                if airDateField.get_attribute("disabled") != "true":
                    airDateField.clear()
                    if updateList[episoideNumber]["air_date"].lower() != "null":
                        airDateField.fill(updateList[episoideNumber]["air_date"])
                    save_submit = True

            if save_submit:
                page.locator("#submit").click()
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
            page.goto(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}")
            time.sleep(3)
            for episoideNumber in importData:
                if (importData[episoideNumber].__contains__("backdrop") and len(importData[episoideNumber]['backdrop']) > 0):
                    css_selector = f"div[class='image'] a[data-episode-number='{episoideNumber}'][data-season-number='{season_number}'] img"
                    if len(page.locator(css_selector).all()) > 0:
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
                    page.goto(f"file:///{image_path}")
                    time.sleep(3)

                    # upload backdrop
                    page.goto(f"https://www.themoviedb.org/tv/{tmdb_id}/season/{season_number}/episode/{episoideNumber}/images/backdrops")
                    if len(page.locator("li[id='no_results']").all()) != 1 and not backdrop_forced_upload:
                        continue

                    page.locator("span[class='glyphicons_v2 circle-empty-plus']").click()
                    time.sleep(random.uniform(1, 2))
                    page.locator("input[id='upload_files']").set_input_files(image_path)
                    page.wait_for_function("() => document.querySelector('span[class=\"k-file-validation-message\"]')?.textContent?.includes('successfully')", timeout=30000)

                    # thumbs up upload backdrop
                except Exception as e:
                    logging.error(
                        f"Download/upload backdrop error for: {importData[episoideNumber]['backdrop']}.", exc_info=e)

    except PlaywrightError as e:
        logging.error(f"Playwright error during episode import: {e}")
        print(f"Browser error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during episode import: {e}")
        print(f"Unexpected error: {e}")
    finally:
        if page:
            try:
                cleanup_playwright_page(page)
            except Exception as e:
                logging.error(f"Failed to cleanup episode import page: {e}")
        
        if config.getboolean('DEFAULT', 'delete_csv_after_import', fallback=False):
            try:
                os.remove(csv_filename)
            except Exception as e:
                logging.error(f"Failed to delete CSV file: {e}")
    
    return
