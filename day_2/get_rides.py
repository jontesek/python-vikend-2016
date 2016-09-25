# -*- coding: utf-8 -*-
import json

from src.RidesGetter import RidesGetter

# Config
r_getter = RidesGetter(json.load(open('configs/redis.json')), json.load(open('configs/gosms.json')))

# Get input data
input_data = {
    'from': u'Praha',
    'to': u'Otrokovice',    # Brno, Frýdek-Místek
    'departure': '2016-10-26',
}

#exit(r_getter.slugify(u'Frýdek-Místek'))

# Get results
parsed_input = r_getter.parse_input(json.dumps(input_data))
rides = r_getter.get_rides(parsed_input['from'], parsed_input['to'], parsed_input['departure'], parsed_input)
print rides

