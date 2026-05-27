import urllib.request
import os
import logging
from .processors.image import process_image
import urllib.parse
def process_image_from_url(type, url, fit_width = -1, fit_height = -1, crop_back = True):
    image_folder = os.path.join(os.getcwd(), "Image")
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    else:
        for imageName in os.listdir(image_folder):
            imagePath = os.path.join(image_folder, imageName)
            os.remove(imagePath)
    fileName = f"{type}.jpg"
    logging.info(f"{fileName} is downloading...")
    image_path = os.path.join(image_folder, fileName)

    urlData = urllib.parse.urlparse(url)
    if urlData.netloc != "":
        if urlData.scheme == "":
            url = "https://" + url
    else:
        if not urlData.scheme.startswith("file"):
            url = "file:///" + url
    urllib.request.urlretrieve(url, image_path)
    process_image(image_path, type, fit_width, fit_height, crop_back)
