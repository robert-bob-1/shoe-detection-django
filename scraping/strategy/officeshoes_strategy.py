

import os

from django.db import IntegrityError
import requests
from bs4 import BeautifulSoup

from evaluate.models import ShoeMetadata, Website
from scraping.strategy.abstract_strategy import AbstractScrapingStrategy
from scraping.strategy.strategy_utils import convert_svg_to_binary


class OfficeShoesScrapingStrategy(AbstractScrapingStrategy):
    website_object = None
    website_name = 'Office Shoes'
    root_url = 'https://www.officeshoes.ro'

    def get_logo(self):
        soup = self.get_page_soup(self.root_url)
        website_logo_link = soup.find('img', alt='Office Shoes').get('src')
        website_logo_xml = requests.get(self.root_url + website_logo_link).content
        website_logo_xml = BeautifulSoup(website_logo_xml, 'xml')
        website_logo_svg = website_logo_xml.find('svg')
        # print(website_logo_svg)
        website_logo_binary = convert_svg_to_binary(website_logo_svg)

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

    def scrape_pages(self, url, _, page_interval_end):
        # for i in range(page_interval_start, page_interval_end + 1):
        page_url = f'{url}{page_interval_end}'
        print(f"URL of the page to scrape: {page_url}")
        self.scrape_page(page_url)

    def scrape_page(self, page_url_with_page_number = ""):
        soup = self.get_page_soup(page_url_with_page_number)

        # Scrape all product links on the page
        # First get the section in order to be more efficient when running find_all
        # For my laptop this saves about 1-1.5 seconds, reducing the average time from 11 seconds to less than 10 seconds
        productlist = soup.find('section', class_='productlist')
        product_cards = productlist.find_all('a', class_='send-search', title=True, id=True)
        product_links = []
        for card in product_cards:
            if card.get('title') == '':
                continue
            product_links.append(card.get('href'))



        for link in product_links:
            print(f"Link of product to scrape: {link}")
            try:
                self.scrape_product(link)
            except IntegrityError as e:
                print(f"Product with url {link} already exists")
                continue
            except Exception as e:
                print(f"Error scraping product with url {link}")
                print(f"Error scraping product: {e}")
                raise Exception(e)


    def scrape_product(self, url):
        soup = self.get_page_soup(url)
        # print(soup)
        shoe_metadata = self.scrape_metadata(soup, url)
        shoe_images = self.scrape_images(soup, shoe_metadata)

        return shoe_metadata, shoe_images

    def scrape_metadata(self, soup, url):
        product_title = soup.find('h1', class_='product_show_title')
        if product_title is None:
            print('Product title not found')
            # log the soup to another file
            with open('soup.html', 'w') as file:
                file.write(str(soup))

            raise Exception('Product title not found')
        # print(product_title)

        # Brand extraction
        brand = product_title.find_all('span', itemprop='name')[0].text.strip()
        print("brand: ", brand)

        # Construct the model name. Also add the brand and color to it since we run into uniqueness issues since the model name does not contain these differentiating factors
        model_name = product_title.find_all('span', itemprop='name')[1].text.strip()
        description_elements = soup.find('div', class_='panel-body').find_all('li')
        model_color = ''
        for li in description_elements:
            if li.text.startswith('Culoare'):
                model_color = li.text.split(':')[1].strip()

        model = f'{brand} {model_name} {model_color}'
        print("model: ", model)


        # Price extraction
        price_text = soup.find('span', property='price').text.strip()
        if price_text is None:
            raise Exception('Price not found')
        price = float(price_text.replace(',', '.').replace(' ', ''))
        print("price: ", price)

        shoeMetadata = ShoeMetadata(name=model, brand=brand, price=price, url=url, website=self.website_object)

        self.save_metadata(shoeMetadata)

        return shoeMetadata


    def scrape_images(self, soup, shoe_metadata):
        all_images = soup.find('div', class_='slick-track').find_all('a')
        print(len(all_images))
        images = []

        for i, image in enumerate(all_images):
            # Skip images with the sole of the shoe and from behind the shoe, since they are extreme edge cases and are unlikely to improve the similarity results
            if i == 1 or i == 4:
                continue

            img_src = image.get('href')

            # Download image
            img_data = requests.get(img_src)

            images.append(img_data.content)

        self.save_images(shoe_metadata, images)

        return images

    def ignore_image(self, i):
        return i == 2 or i == 5

