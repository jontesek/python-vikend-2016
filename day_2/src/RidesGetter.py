# -*- coding: utf-8 -*-
import re
import datetime
import json

from unidecode import unidecode
from redis import StrictRedis

from StudentAgencyParser import StudentAgencyParser
from SmsMailer import SmsMailer


class RidesGetter(object):

    def __init__(self, redis_config, sms_config):
        self.sa_parser = StudentAgencyParser()
        self.redis = StrictRedis(**redis_config)
        self.sms_mailer = SmsMailer(**sms_config)

    def parse_input(self, json_string):
        json_dict = json.loads(json_string)
        return {
            'from': json_dict['from'],
            'to': json_dict['to'],
            'departure': datetime.datetime.strptime(json_dict['departure'], '%Y-%m-%d')
        }

    def get_rides(self, from_city_name, to_city_name, departure_date, input_data):
        # Get city IDs
        id_from, id_to = self._get_two_city_ids(from_city_name, to_city_name)

        # Search Redis for connection
        connection_key = 'connection_{0}_{1}_{2}'.format(id_from, id_to, departure_date.strftime('%Y%m%d'))
        rides = self.redis.get(connection_key)

        if not rides or rides == '[]':
            print('Connection data not found in Redis.')
            # Get data from Studentagency
            rides = self.sa_parser.get_rides(id_from, id_to, input_data)
            # Save it to Redis
            if rides:
                rides = json.dumps(rides)
                self.redis.set(connection_key, rides)

        # Result
        return rides

    def check_seats(self, input_data, book_free_seats, mobile_send_number):
        id_from, id_to = self._get_two_city_ids(input_data['from'], input_data['to'])
        #res_number = self.sa_parser.get_rides(id_from, id_to, input_data, book_free_seats)
        res_number = 24543
        msg = ('Seat freed for bus on {0}. Reservation: {1}'
               .format(input_data['departure'].strftime('%d.%m.%Y'), res_number))
        resp_code = self.sms_mailer.send_sms(msg, mobile_send_number)
        if resp_code != 200:
            return 'Error while sending SMS: {0}'.format(resp_code)
        print msg
        return res_number


    def _get_two_city_ids(self, from_city_name, to_city_name):
        # Search Redis for city IDs
        id_from = self.redis.get('city_id_{0}'.format(self.slugify(from_city_name)))
        id_to = self.redis.get('city_id_{0}'.format(self.slugify(to_city_name)))

        # If IDs were not found in Redis.
        if not id_from or not id_to:
            print('Cities not found in Redis.')
            cities = self.sa_parser.get_all_city_ids()
            id_from, id_to = self.sa_parser.get_two_city_ids(cities, from_city_name, to_city_name)
            self.redis.set('city_id_{0}'.format(self.slugify(from_city_name)), id_from)
            self.redis.set('city_id_{0}'.format(self.slugify(to_city_name)), id_to)
            return id_from, id_to
        else:
            return id_from, id_to


    def slugify(self, s):
        """
        Remove diacritic from input string and replace all non alphanumeric symbols with underscore.
        Frýdek-Místek -> frydek_mistek
        """
        s = unidecode(s).lower()
        return re.sub(r'\W+', '_', s)
