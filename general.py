from notifier import Notifier
from parser import Parser, webdriver
from binance_parser import BinanceParser
from config import *
from time import sleep


def mutate(summaries, bin_prices, straight_cost):
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
            'asset_price': float(def_price),
            'binance_price': float(binance_price),
            'cross_price': cross_price,
            'straight_price': float(straight_cost),
            'profit': ((float(straight_cost) / cross_price) - 1) * 100
        }
        final.append(info)
    return final


def get_straight_cost(driver: webdriver.Chrome):
    found = False
    while not found:
        try:
            print('getting p2p price\n')
            driver.get('https://p2p.binance.com/ru/trade/Tinkoff/USDT?fiat=RUB')
            sleep(10)
            try:
                driver.find_element_by_xpath("/html/body/div[8]/div/div[2]/button[1]").click()
            except:
                pass
            try:
                selects = driver.find_elements_by_xpath('//*[@id="onetrust-consent-sdk"]/div[1]')
                for select in selects:
                    driver.execute_script("arguments[0].setAttribute('class', 'onetrust-pc-dark-filter ot-hide ot-fade-in')", select)
            except:
                pass
            try:
                driver.find_element_by_css_selector('body > div.css-vp41bv > div > svg').click()
            except:
                pass
            element = driver.find_element_by_id('onetrust-style')
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
                """, element)
            #driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[4]/div/div[1]/div[3]/div[2]/div[1]").click()
            #driver.find_element_by_xpath('//*[@id="Тинькофф"]/div/div[2]').click()
            print('Беру значения!')
            sleep(5)
            try:
                vurnku = driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[1]/div[4]/div/div[2]/div[1]/div[1]/div[2]/div/div").text
                vurnku = vurnku.split('\n')[0] 
            except:
                print('Wrong path')
            print(vurnku)
            if vurnku is not None:
                found = True
            else:
                print("Ошибка!")
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

    binance_parser = BinanceParser('', '')
    while True:
        summaries = parser.parse()
        if summaries == 'chill':
           print('Chilling 60 secs')
           sleep(60)
           continue
        straight_cost = get_straight_cost(parser.driver)
        print(straight_cost)
        bin_prices = binance_parser.get_all_tickers(summaries)
        final = mutate(summaries, bin_prices, straight_cost)
        notifier.work(final)
        sleep(200)


# if __name__ == '__main__':
#     main(0)
