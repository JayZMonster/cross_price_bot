from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from random import randint
from time import sleep


class Parser:

    def __init__(self, url, asset, tickers):
        self.url = url
        self.asset = asset
        self.tickers: list = tickers
        self.driver = None
        # There might be some problems with initializing it in linux
        try:
            self.init_driver()
        except:
            sleep(5)
            self.init_driver()

    def init_driver(self, wind=False):
        """
        Initializing webdriver as Edge for Windows or Chrome for linux
        """
        # msedge driver for windows
        if wind:
            self.driver = webdriver.Edge()
        else:
            # Chrome driver for linux
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=chrome_options)

    def quit_driver(self):
        self.driver.quit()

    def parse_page(self, sub=''):
        """
        Getting page via webdriver
        """
        found = False
        while not found:
            try:
                print('First try')
                self.driver.get('view-source:' + self.url + sub)
                found = True
            except:
                try:
                    print('Second try')
                    self.driver.get(self.url + sub)
                    found = True
                except:
                    print('Unable to parse now!')
                    sleep(5)
                    continue
            content = self.driver.find_element_by_tag_name('body').text
            soup = BeautifulSoup(content, 'lxml')
            return soup

    def parse(self):
        """
        Looking for the best exchange offer in each of tickers from the list, returning summary
        """
        # Parsing ticker's pages
        summaries = []
        for ticker in self.tickers:
            if ticker["name"] == 'bittorrent':
                break
            print(f'Parsing {ticker["name"]}...')
            # Creating a unique url for each pair
            new_url = f'{self.asset}-to-{ticker["name"]}.html'
            try:
                # Looking for the best exchange offer
                page = self.parse_page(new_url)
                exchanges = page.find('div', {'id': 'rates_block'})
                best = exchanges.find('tbody').find('tr')
                best_link = best.find('a').get('href')
                price_amount = best.find_all('td', {'class': 'bi'})
                best_price = ''.join(price_amount[0].text.split(' RUB ')[0].split(' '))
                best_amount = price_amount[1].text.split(' ')[0]
                price = float(best_price) / float(best_amount)
            except:
                print('Skipped!')
                continue
            summaries.append({
                'ticker': ticker,
                'link': best_link,
                'price': price,
            })
            sleep(randint(3, 6))
        return summaries


# if __name__ == '__main__':
#     parser = Parser('https://www.bestchange.ru/', 'qiwi')
#     msg = parser.parse()
#     print(msg)
