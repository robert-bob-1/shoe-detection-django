from bs4 import BeautifulSoup
import requests
import os

from selenium import webdriver

driver = webdriver.Chrome()

# Method to scrape product page for photos
def scrape_product_photos(url):
    # Open a Chrome page with the given URL and get the html from the source
    driver.get(url)
    page_source = driver.page_source

    # Parse the HTML
    soup = BeautifulSoup(page_source, 'html.parser')

    if not os.path.exists('photos'):
        os.makedirs('photos')

    # Find all the images on the page
    images = soup.find_all('img')

    # Iterate through the images and download the ones with width > 300
    for i, image in enumerate(images):
        try:
            img_width = int(image.get('width', 0))
            if img_width > 300:
                img_src = image.get('src')
                img_name = f'photos/{i}.jpg'
                # Download image
                img_data = requests.get(img_src)

                with open(img_name, 'wb') as file:
                    file.write(img_data.content)
                print(f"Downloaded {img_name}")
        except Exception as e:
            print(f"Error downloading image {i}: {e}")
            # Ignore images with invalid width
            pass

# Script to get all product pages' links in a page of a website (epantofi in this case; adjust class name for other websites)
def scrape_product_urls(url):
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