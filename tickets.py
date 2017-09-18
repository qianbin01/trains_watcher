"""命令行火车票查看器

Usage:
    tickets  <from> <to> <date>

Examples:
    tickets 上海 北京 2016-10-10
    tickets 成都 南京 2016-10-10
"""
import requests
from docopt import docopt
from prettytable import PrettyTable
from colorama import init, Fore
from pinyin import getpinyin
from bs4 import BeautifulSoup

init()


class TrainsCollection:
    header = '车次 车站 时间 历时 二等 二等价格 一等 一等价格 商务 商务价格 无座 无座价格'.split()

    def __init__(self, available_trains):
        self.available_trains = available_trains

    def _get_duration(self, raw_train):
        duration = raw_train['TakeTime']
        return duration

    def _get_detail_seat(self, raw_train):
        seats = raw_train['SeatBookingItem']
        my_seat = {}
        for seat in seats:
            if seat['SeatTypeId'] == 209:  # 二等座
                my_seat['two'] = seat['Inventory']
                my_seat['two_price'] = seat['Price']
            elif seat['SeatTypeId'] == 207:  # 一等座
                my_seat['one'] = seat['Inventory']
                my_seat['one_price'] = seat['Price']
            elif seat['SeatTypeId'] == 221:  # 商务座
                my_seat['bus'] = seat['Inventory']
                my_seat['bus_price'] = seat['Price']
            elif seat['SeatTypeId'] == 227:  # 无座
                my_seat['noseat'] = seat['Inventory']
                my_seat['noseat_price'] = seat['Price']
        return my_seat

    @property
    def trains(self):
        for raw_train in self.available_trains:
            train_no = raw_train['TrainName']
            train_seat = self._get_detail_seat(raw_train)
            train = [
                train_no,
                '\n'.join([Fore.GREEN + raw_train['StartStationName'] + Fore.RESET,
                           Fore.RED + raw_train['EndStationName'] + Fore.RESET]),
                '\n'.join([Fore.GREEN + raw_train['StratTime'] + Fore.RESET,
                           Fore.RED + raw_train['EndTime'] + Fore.RESET]),
                self._get_duration(raw_train),
                train_seat.get('two', '无'),
                train_seat.get('two_price', '无'),
                train_seat.get('one', '无'),
                train_seat.get('one_price', '无'),
                train_seat.get('bus', '无'),
                train_seat.get('bus_price', '无'),
                train_seat.get('noseat', '无'),
                train_seat.get('noseat_price', '无'),
            ]
            yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


def cli():
    arguments = docopt(__doc__)
    from_station = getpinyin(arguments['<from>'])
    to_station = getpinyin(arguments['<to>'])
    date = arguments['<date>']
    url = 'http://trains.ctrip.com/TrainBooking/Ajax/SearchListHandler.ashx?Action=getSearchList'
    data = {
        'value': '{"IsBus":false,"Filter":"0","IsGaoTie":true,"IsDongChe":true,'
                 '"DepartureCity":' + from_station + ','
                                                     '"ArrivalCity":' + to_station + ','
                                                                                     '"DepartureCityName":' + arguments[
                     "<from>"] + ','
                                 '"ArrivalCityName":' + arguments["<to>"] + ','
                                                                            '"DepartureDate":' + date + '}'
    }
    r = requests.post(url, data=data)
    available_trains = r.json()['TrainItemsList']
    TrainsCollection(available_trains).pretty_print()


if __name__ == '__main__':
    cli()
