# -*- coding: utf-8 -*-
import re
import datetime
import json

from unidecode import unidecode
from grab import Grab


class StudentAgencyParser(object):

    def __init__(self):
        self.g = Grab()
        self.dtformat = '%Y%m%d'

    def get_all_city_ids(self, country_code='CZ'):
        self.g.go('https://jizdenky.studentagency.cz')
        all_dest_dict = self.g.go('https://www.studentagency.cz/data/wc/ybus-form/destinations-cs.json')
        cities = []
        for dest in all_dest_dict.json['destinations']:
            if dest['code'] == country_code:
                cities = dest['cities']
                break
        return cities

    def get_two_city_ids(self, cities, city_from, city_to):
        id_from, id_to = None, None
        for city in cities:
            if city['name'] == city_from:
                id_from = city['id']
            elif city['name'] == city_to:
                id_to = city['id']
            if id_from and id_to:
                break
        return id_from, id_to

    def get_rides(self, id_from, id_to, input_data, book_free_seats=False):
        departure_date = input_data['departure']
        # Homepage request
        self.g.go('https://jizdenky.studentagency.cz')
        # Request 1
        url = (
            'https://jizdenky.regiojet.cz/Booking/from/{0}/to/{1}/tarif/REGULAR/departure/{2}/retdep/{3}/return/false'
            .format(id_from, id_to, departure_date.strftime(self.dtformat), departure_date.strftime(self.dtformat))
        )
        self.g.go(url)
        # Request 2
        url = (
            'https://jizdenky.regiojet.cz/Booking/from/{0}/to/{1}/tarif/REGULAR/departure/{2}/retdep/{3}/return/false'
            '?1-1.IBehaviorListener.0-mainPanel-routesPanel&_=1474659041806'
            .format(id_from, id_to, departure_date.strftime(self.dtformat), departure_date.strftime(self.dtformat))
        )
        self.g.go(url)
        # Process response
        return self._process_rides_response(id_from, id_to, input_data, book_free_seats)

    def _process_rides_response(self, id_from, id_to, input_data, book_free_seats=False):
        rides = self.g.css_list('div.item_blue[ybus\:rowid^="{0}"]'.format(input_data['departure'].strftime(self.dtformat)))

        #print('Number of rides: {0}'.format(len(rides)))

        all_rides = []

        for r_n, ride in enumerate(rides, start=1):
            data = {
                'from': id_from,
                'to': id_to,
            }
            # Departure time
            dep_time_str = ride.cssselect('div.col_depart')[0].text
            dep_time_list = dep_time_str.split(':')
            dep_dtime = datetime.datetime(input_data['departure'].year, input_data['departure'].month, input_data['departure'].day,
                                          int(dep_time_list[0]), int(dep_time_list[1]))
            data['departure'] = dep_dtime.strftime('%Y-%m-%d %H:%M')
            # Arrival time
            arr_time_str = ride.cssselect('div.col_arival')[0].text
            dep_time_list = arr_time_str.split(':')
            dep_dtime = datetime.datetime(input_data['departure'].year, input_data['departure'].month, input_data['departure'].day,
                                          int(dep_time_list[0]), int(dep_time_list[1]))
            data['arrival'] = dep_dtime.strftime('%Y-%m-%d %H:%M')
            # Type
            img_type = ride.xpath('./div[@class="col_icon"]/a/img')[0].get('title')
            if img_type == 'Autobus':
                data['type'] = 'bus'
            elif img_type == 'Vlak':
                data['type'] = 'train'
            elif img_type == 'Autobus / Vlak':
                data['type'] = 'bus/train'
            # Lowest price
            price_str = ride.cssselect('div.col_price_no_basket_image')
            if price_str:
                price_str = price_str[0].text_content().strip()
                price_numbers = re.findall('\d+', price_str)
                data['price'] = float(price_numbers[0])
            else:
                price_str = ride.cssselect('div.col_price')[0].text_content()
                data['price'] = float(re.findall('\d+', price_str)[0])
            # City names
            data['from_name'] = input_data['from']
            data['to_name'] = input_data['to']
            # Seats
            seats_str = ride.cssselect('div.col_space')[0].text
            seats_num = int(re.findall('\d+', seats_str)[0])
            data['seats'] = seats_num
            # Book free seat?
            if seats_num == book_free_seats:
                print('Booking ticket! {0}'.format(str(data)))
                return self.create_reservation(id_from, id_to, input_data['departure'], r_n)
            # Insert data
            all_rides.append(data)
        # Result
        return all_rides


    def create_reservation(self, id_from, id_to, departure_date, route_view_number):
        # REQ 1 - Add ticket
        url = ('https://jizdenky.regiojet.cz/Booking/from/{0}/to/{1}/tarif/REGULAR/departure/{2}/retdep/{3}'
               '/return/false?1-1.IBehaviorListener.0-mainPanel-routesPanel-content-outwardpanel-routesList-panel~content-'
               'routesView-1-routeView-{4}-routeSummary-sidePanel&_=1474795086808'
               .format(id_from, id_to, departure_date.strftime(self.dtformat), departure_date.strftime(self.dtformat), route_view_number))
        self.g.go(url)
        # Set cookies
        self.g.cookies.set(name='ybus.czCookiePolicyAccepted', value='1', domain='jizdenky.regiojet.cz', path='/')
        self.g.load_cookies()
        # REQ 2 - Order whole basket
        url = ('https://jizdenky.regiojet.cz/Booking/from/{0}/to/{1}/tarif/REGULAR/departure/{2}/retdep/{3}'
               '/return/false?1-1.ILinkListener-basketPanel-orderButton'
               .format(id_from, id_to, departure_date.strftime(self.dtformat), departure_date.strftime(self.dtformat)))
        self.g.go(url)
        #self.g.go(self.g.response.url)
        self.g.response.browse()
        # REQ 3 - Choose seat and agree to terms
        url = ('https://jizdenky.regiojet.cz/Purchase?3-1.IFormSubmitListener-bookingWizard-wizardStepContent-mainForm')
        post_data = {
            'id1ac_hf_0': '',
            'bottomComponent:accountPhonePanel:stylablePanel:accountPhone:': '',
            'bottomComponent:termsAgreementCont:termsAgreementCB': 'on',
            'buttonContainer:createTicketButton': '',
        }
        self.g.setup(post=post_data)
        self.g.go(url)
        # Get reservation number
        self.g.response.browse()
        res_number = self.g.doc.select('//div[@id="ticketPage"]/h1/span')[0].text
        return res_number
