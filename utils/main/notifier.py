import requests
from typing import List
from utils.config import take_profit, TG_TOKEN


class Notifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        # Notify every user that bot is up
        for i in range(len(TG_TOKEN)):
            self.notify('Бот работает!', i)

    def notify(self, msg, num):
        """
        Sends message to every user via telegram api, it is required to specify which bot to use
        """
        url = f"https://api.telegram.org/bot{self.token[num]}/sendMessage"
        for i in self.chat_id:
            msg_data = {
                'chat_id': self.chat_id,
                'text': msg,
                'parse_mode': 'Markdown'
            }
            requests.post(url, data=msg_data)

    def work(self, info: List[dict]):
        """
        Generates a message for each summary and notifies about profitable
        """
        for i in info:
            msg = f'Коридор (БЧ+Бинанс): RUB QIWI->{i["ticker"]["ticker"]}->USDT\n' \
                  f'[Bestchange]({i["link"]}): Отдаем {i["asset_price"]} RUB QIWI -> Получаем' \
                  f' 1 {i["ticker"]["ticker"]}\n' \
                  f'Binance: Отдаем 1 {i["ticker"]["ticker"]} -> Получаем {i["binance_price"]} USDT\n' \
                  f'Binance P2P: {i["straight_price"]}\n' \
                  f'Кросс-курс: {i["cross_price"]}\n' \
                  f'Выгода: {round(i["profit"], 2)}%\n'
            print(msg)
            # config has take-profit list
            if take_profit[0] < i['profit'] < take_profit[1] :
                self.notify(msg, 0)
            if i['profit'] > take_profit[1]:
                self.notify(msg, 1)
