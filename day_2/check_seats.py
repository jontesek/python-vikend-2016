# -*- coding: utf-8 -*-
import json

from src.RidesGetter import RidesGetter

# Config
r_getter = RidesGetter(json.load(open('configs/redis.json')), json.load(open('configs/gosms.json')))

# Get input data
input_data = {
    'from': u'Praha',
    'to': u'Brno',    # Brno, Frýdek-Místek
    'departure': '2016-11-09',
}

# Get results
parsed_input = r_getter.parse_input(json.dumps(input_data))
result = r_getter.check_seats(parsed_input, 52, '+420000000000')
print result
