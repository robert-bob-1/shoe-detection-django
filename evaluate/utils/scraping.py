from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
from django.core.files.base import ContentFile

from evaluate.models import ShoeImage, ShoeMetadata
# from shoe_detection_web_app.scraping.exceptions import DuplicateProductException

photos_dir = 'photos/'


def scrape_product_photos(soup, product_name):
    # Find all the images on the page
    all_images = soup.find_all('img')

    product_images = []

    image_count = 0
    # Iterate through the images and download the ones with width > 300
    for i, image in enumerate(all_images):
        try:
            img_width = int(image.get('width', 0))
            if img_width > 300:  # value selected to exclude other low res shoes. No other relevant attributes to differentiate other than width
                img_src = image.get('src')
                # img_name = f'{photos_dir}{product_name}_{image_count}.jpg'
                # image_count += 1
                # Download image
                img_data = requests.get(img_src)

                product_images.append(img_data.content)
                # with open(img_name, 'wb') as file:
                #     file.write(img_data.content)
                # print(f"Downloaded {img_name}")
        except Exception as e:
            print(f"Error downloading image {i}: {e}")
            # Ignore images with invalid width
            pass
    return product_images


# Method to scrape product page for photos
def scrape_product_object(url):
    driver = webdriver.Chrome()
    # Open a Chrome page with the given URL and get the html from the source
    driver.get(url)
    page_source = driver.page_source
    # Parse the HTML
    soup = BeautifulSoup(page_source, 'html.parser')

    product_name = soup.find('strong', class_='product-name').text.strip().replace(' ', '-')
    print(product_name)
    # if ShoeMetadata.objects.filter(name=product_name).exists():
        # raise DuplicateProductException(f"Product with name {product_name} already exists")

    product_brand = soup.find('strong', class_='brand-name').text.strip()
    print(product_brand)

    price = soup.find('div', class_='final-price').text.replace('Lei', '').strip()
    price = price.replace('.', '')
    price = price.replace(',', '.')
    price = float(price)
    print(price)

    shoeMetadata = ShoeMetadata(name=product_name, brand=product_brand, price=price, url=url)


    product_images = scrape_product_photos(soup, product_name)


    return shoeMetadata, product_images


# Script to get all product pages' links in a page of a website (epantofi in this case; adjust class name for other websites)
def scrape_product_urls(url):
    driver = webdriver.Chrome()
    driver.get(url)
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    # test fetching one url
    product_links = soup.find_all('a', class_='product-card-link')
    product_hrefs = []
    for link in product_links:
        product_hrefs.append('https://epantofi.ro' + link.get('href'))

    print(product_hrefs[0:3])
    return product_hrefs

def scrape_product_object_and_save(url):
    shoe_metadata = None
    shoe_images = []
    shoe_images_ids = []
    image_files = []
    try:
        print(url)
        shoe_metadata, shoe_images = scrape_product_object(url)
    # except DuplicateProductException as e:
    #     raise DuplicateProductException(e)
    except Exception as e:
        raise Exception(f"Error scraping product: {e}")

    # Save the shoe metadata and shoe images
    try:
        shoe_metadata.save()
        for i in range(len(shoe_images)):
            # skip the 4th image as it is almost always the sole of the shoe
            if i == 3:
                continue
            image_files.append(shoe_images[i])
            # Old rendition of saving image in ImageField
            image_file = ContentFile(shoe_images[i])
            image_file.name = f'{shoe_metadata.name}_{i}.jpg'


            shoe_image = ShoeImage(shoe=shoe_metadata, image=shoe_images[i], image_local=image_file)
            shoe_image.save()
            shoe_images_ids.append(shoe_image.id)

    except Exception as e:
        raise Exception(f"Error saving product: {e}")

    return shoe_metadata, image_files, shoe_images_ids
