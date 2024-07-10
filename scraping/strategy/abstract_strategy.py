from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from evaluate.utils.cpp_service import compute_CPP_properties_and_save
from evaluate.utils.database import save_image_classification_data, save_product_classification_data
from evaluate.utils.image_processing import extract_shoe_info_from_image
from evaluate.models import ShoeImage

class AbstractScrapingStrategy(ABC):
    @property
    @abstractmethod
    def website_object(self):
        pass

    @property
    @abstractmethod
    def website_name(self):
        pass

    @property
    @abstractmethod
    def root_url(self):
        pass

    @abstractmethod
    def scrape_pages(self, url, page_interval_start, page_interval_end, page_number_url_suffix):
        """ Scrape all products from given pages, if website supports simple url page changes. """
        """ page_number_url_suffix is the suffix added between the url and the page number to trigger a page change."""
        pass

    @abstractmethod
    def scrape_page(self, url):
        """ Scrape all products from a page. """
        pass

    @abstractmethod
    def scrape_product(self, url):
        """ Scrape a whole product (metadata + images) from a product page. """
        pass

    @abstractmethod
    def scrape_metadata(self, soup):
        """ Scrape shoe metadata from a product page. (name, brand, price, url) """
        pass

    @abstractmethod
    def scrape_images(self, soup):
        """ Scrape shoe images from a product page. """
        pass

    @abstractmethod
    def ignore_image(self, i):
        """ Ignore image at index i in case it is unrepresentative for the shoe (if shoes at a given position are always the sole of the shoe for example). """
        pass

    def get_page_soup(self, url):
        """ Get the soup of the page from the given URL. """

        # Open a Chrome page with the given URL and get the html from the source
        driver = webdriver.Chrome(service=Service('C:\\Users\\rober\\.cache\\selenium\\chromedriver\\win64\\126.0.6478.63\\chromedriver.exe'))
        driver.get(url)
        page_source = driver.page_source
        driver.quit()

        # Parse the HTML and return soup object
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup

    def save_metadata(self, shoe_metadata):
        """ Save the metadata in the database. """
        try:
            shoe_metadata.save()
        except IntegrityError as e:
            print(f"Error saving metadata: {e}")
            raise IntegrityError(f"Error saving metadata: {e}")
        except Exception as e:
            print(f"Error saving metadata: {e}")
            raise Exception(f"Error saving metadata: {e}")

    def save_images(self, shoe_metadata, shoe_images):
        """ Save the images in the database. """
        all_classification_data = []
        for i in range(len(shoe_images)):
            # Skip the nth image if it is unrepresentative for the shoe (if it is in a strange/unnatural position)
            if self.ignore_image(i):
                continue


            # The next two lines are only used for quicker visualization of images.
            # They save the image in the photos directory and save the path in the image_local column.
            # Comment these out if you don't need to visualize the images.
            image_file = ContentFile(shoe_images[i])
            image_file.name = f'{shoe_metadata.name}_{i}.jpg'

            shoe_image = ShoeImage(shoe=shoe_metadata, image=shoe_images[i], image_local=image_file)
            shoe_image.save()
            print(f"Saved image {i} for {shoe_metadata.name}")

            extracted_shoe, sorted_classification_data = extract_shoe_info_from_image(
                shoe_image.image,
                DISPLAY_IMAGES=False
            )

            save_image_classification_data(shoe_image.id, sorted_classification_data)
            all_classification_data.append(sorted_classification_data)

            compute_CPP_properties_and_save(extracted_shoe, shoe_image.id)

        save_product_classification_data(shoe_metadata, all_classification_data)

        return all_classification_data


