import urllib.request
import os
import logging
from .processors.image import process_image
def process_image_from_url(type, url):
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
    urllib.request.urlretrieve(url, image_path)
    process_image(image_path, type)
