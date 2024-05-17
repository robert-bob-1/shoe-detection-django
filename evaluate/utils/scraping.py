from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver

from evaluate.models import ShoeMetadata

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
                img_name = f'{photos_dir}{product_name}_{image_count}.jpg'
                image_count += 1
                # Download image
                img_data = requests.get(img_src)

                product_images.append(img_data.content)
                # with open(img_name, 'wb') as file:
                #     file.write(img_data.content)
                print(f"Downloaded {img_name}")
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

    if not os.path.exists('photos'):
        os.makedirs('photos')

    product_name = soup.find('strong', class_='product-name').text.strip().replace(' ', '-')
    print(product_name)

    product_brand = soup.find('strong', class_='brand-name').text.strip()
    print(product_brand)

    price = soup.find('div', class_='final-price').text.replace('Lei', '').strip()
    price = price.replace(',', '.')
    price = float(price)
    print(price)

    product_images = scrape_product_photos(soup, product_name)

    shoeMetadata = ShoeMetadata(name=product_name, images=product_images, price=price, url=url)

    return shoeMetadata


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
