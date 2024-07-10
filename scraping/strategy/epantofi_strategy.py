

import os

from django.db import IntegrityError
import requests
from evaluate.models import ShoeMetadata, Website
from scraping.strategy.abstract_strategy import AbstractScrapingStrategy
from scraping.strategy.strategy_utils import convert_svg_to_binary


class EPantofiScrapingStrategy(AbstractScrapingStrategy):
    website_object = None
    website_name = 'ePantofi'
    root_url = 'https://www.epantofi.ro'
    logo_height = 79
    logo_width = 352

    def get_logo(self):
        soup = self.get_page_soup(self.root_url)
        website_logo_svg = soup.find('svg', class_='main-logo')
        # print(website_logo_svg)
        website_logo_binary = convert_svg_to_binary(website_logo_svg, width=self.logo_width, height=self.logo_height)

        return website_logo_binary

    def __init__(self) -> None:
        super().__init__()
        if self.website_object is None:
            try:
                self.website_object = Website.objects.get(name=self.website_name)

                if self.website_object.logo is None or self.website_object.logo == b'':
                    print('Website exists in the database, but the logo is missing, scraping website')

                    self.website_object.logo = self.get_logo()
                    self.website_object.save()

            except Website.DoesNotExist:
                print('Website does not exist in the database, scraping website')

                website_logo_binary = self.get_logo()

                self.website_object = Website(name=self.website_name, url=self.root_url, logo=website_logo_binary)
                self.website_object.save()

    def scrape_pages(self, url, page_interval_start, page_interval_end):
        for i in range(page_interval_start, page_interval_end + 1):
            page_url = f'{url}{i}'
            print(f"URL of the page to scrape: {page_url}")
            self.scrape_page(page_url_with_page_number=page_url)
        pass

    def scrape_page(self, page_url_with_page_number = ""):
        soup = self.get_page_soup(page_url_with_page_number)

        # Scrape all product links on the page
        product_links = soup.find_all('a', class_='product-card-link')

        for link in product_links:
            print(f"Link: {link.get('href')}")
            product_url = self.root_url + link.get('href')
            print(f"Product_url to scrapeafter os.path.join() {product_url}")

            try:
                self.scrape_product(product_url)
            except IntegrityError as e:
                print(f"Product with url {product_url} already exists")
                continue
            except Exception as e:
                print(f"Error scraping product: {e}")
                raise Exception(e)
        pass

    def scrape_product(self, url):
        soup = self.get_page_soup(url)
        shoe_metadata = self.scrape_metadata(soup, url)
        shoe_images = self.scrape_images(soup, shoe_metadata)

        return shoe_metadata, shoe_images

    def scrape_metadata(self, soup, url):
        name = soup.find('strong', class_='product-name').text.strip().replace(' ', '-')

        brand = soup.find('strong', class_='brand-name').text.strip()

        price = soup.find('div', class_='final-price').text.replace('Lei', '').strip()
        price = price.replace('.', '')
        price = price.replace(',', '.')
        price = float(price)

        shoeMetadata = ShoeMetadata(name=name, brand=brand, price=price, url=url)

        self.save_metadata(shoeMetadata)

        return shoeMetadata


    def scrape_images(self, soup, shoe_metadata):
        all_images = soup.find_all('img')
        images = []

        for _, image in enumerate(all_images):
            img_width = int(image.get('width', 0))

            # value selected to exclude other low res shoes. No other relevant attributes to differentiate between images on the page other than image size
            if img_width > 300:
                img_src = image.get('src')

                # Download image
                img_data = requests.get(img_src)

                images.append(img_data.content)

        self.save_images(shoe_metadata, images)

        return images

    def ignore_image(self, i):
        return i == 3

