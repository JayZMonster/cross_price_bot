from utils.main.notifier import Notifier
from utils.main.parser import Parser, webdriver
from utils.main.binance_parser import BinanceParser
from utils.config import *
from time import sleep


def mutate(summaries, bin_prices, straight_cost):
    """
    Mixing all the summaries with binance prices and p2p prices
    """
    final = []
    for summar, bin_ in zip(summaries, bin_prices):
        try:
            binance_price = bin_['price']
            def_price = summar['price']
            cross_price = round(float(summar['price']) / float(bin_['price']), 3)
        except:
            cross_price = -1
            binance_price = 0
            def_price = 0
        info = {
            'link': summar['link'],
            'ticker': summar['ticker'],
            'asset_price': float(def_price), # 3rd party exchanges price
            'binance_price': float(binance_price), # price to exchange currency on binance
            'cross_price': cross_price, # cross-price
            'straight_price': float(straight_cost), # price of USDT on p2p
            'profit': ((float(straight_cost) / cross_price) - 1) * 100
        }
        final.append(info)
    return final


def get_straight_cost(driver: webdriver.Chrome):
    """
    Getting p2p price of USDT in RUB
    """
    found = False
    while not found:
        try:
            print('getting p2p price\n')
            driver.get('https://p2p.binance.com/ru/trade/buy/USDT?fiat=RUB&payment=TINKOFF')
            sleep(10)
            # Trying to click the button to close possible popup
            try:
                driver.find_element_by_xpath("/html/body/div[8]/div/div[2]/button[1]").click()
            except:
                pass
            # Trying to change class of element to provide an access to the site
            try:
                selects = driver.find_elements_by_xpath('//*[@id="onetrust-consent-sdk"]/div[1]')
                for select in selects:
                    driver.execute_script("arguments[0].setAttribute('class', 'onetrust-pc-dark-filter ot-hide ot-fade-in')", select)
            except:
                pass
            # Trying to close another possible popup, only available with css selector
            try:
                driver.find_element_by_css_selector('body > div.css-vp41bv > div > svg').click()
            except:
                pass
            # Removing element from page to get an access
            element = driver.find_element_by_id('onetrust-style')
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
                """, element)
            # Clicking on bar to choose bank
            driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[4]/div/div[1]/div[3]/div[2]/div[1]").click()
            # Clicking on Tinkoff
            driver.find_element_by_xpath('//*[@id="Тинькофф"]/div/div[2]').click()
            sleep(5)
            # Waiting for loading, then looking for the best offer
            vurnku = driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[5]/div/div[2]/div[1]/div[1]/div[2]/div/div/div[1]").text

            if vurnku is not None:
                found = True
            else:
                raise Exception
        except:
            sleep(5)
            continue
    return vurnku


def main(num):
    print(f'Started bot with list of names:\n{proc_lists[num]}')
    notifier = Notifier(token=TG_TOKEN,
                        chat_id=CHAT_ID,
                        )
    parser = Parser(url=URL,
                    asset=ASSET,
                    tickers=proc_lists[num],
                    )
    # you may place here your api keys but it is unnecessary
    binance_parser = BinanceParser('', '')
    # Main cycle
    while True:
        # parsing ticker's pages
        summaries = parser.parse()
        if summaries == 'chill':
           print('Chilling 60 secs')
           sleep(60)
           continue
        # parsing USDT cost on p2p
        straight_cost = get_straight_cost(parser.driver)
        print(straight_cost)
        # Getting prices from binance
        bin_prices = binance_parser.get_all_tickers(summaries)
        # Mixing all we've got
        final = mutate(summaries, bin_prices, straight_cost)
        # Notifying
        notifier.work(final)
        sleep(200)


# if __name__ == '__main__':
#     main(0)
