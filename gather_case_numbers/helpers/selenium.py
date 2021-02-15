from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumScraper:
    __driver = None
    __options = ['ignore-certificate-errors', 'incognito', 'headless']

    def __init__(self):
        if SeleniumScraper.__driver != None:
            raise Exception("Cannot create another instance. Access existing instance with get_driver() method.")
        else:
            print('Creating a singleton instance of the selenium Chrome driver')
            SeleniumScraper.__driver = self.__create_driver()

    def __create_driver(self):
        options = webdriver.ChromeOptions()
        for option in self.__options:
            options.add_argument(f'--{option}')

        return webdriver.Chrome(ChromeDriverManager().install(), options=options)

    @staticmethod
    def get_driver():
        if SeleniumScraper.__driver == None:
            SeleniumScraper()

        return SeleniumScraper.__driver
