# -*- coding: utf-8 -*-
import re

from grab import Grab
import time

g = Grab()

g.go('https://jizdenky.studentagency.cz')

g.go('https://jizdenky.regiojet.cz/Booking/from/10202003/to/372842002/tarif/REGULAR/departure/20160928/retdep/20160928/return/false')

g.go('https://jizdenky.regiojet.cz/Booking/from/10202003/to/372842002/tarif/REGULAR/departure/20160928/retdep/20160928/return/false?1-1.IBehaviorListener.0-mainPanel-routesPanel&_=1474659041806')

#g.response.browse()

rides = g.css_list('div.item_blue')

print('Number of rides: {0}'.format(len(rides)))

# print type(rides[0])

routes_details = g.css_list('div.routeDetail')

for r_i, ride in enumerate(rides):
    data = {
        'depart': ride.cssselect('div.col_depart')[0].text,
        'arrival': ride.cssselect('div.col_arival')[0].text,
    }
    space_str = ride.cssselect('div.col_space')[0].text
    data['space_count'] = re.findall('\d+', space_str)[0]
    price_str = ride.cssselect('div.col_price_no_basket_image')[0].text_content().strip()
    price_numbers = re.findall('\d+', price_str)
    data['min_price'] = price_numbers[0]
    data['max_price'] = price_numbers[1]
    data['route_id'] = routes_details[r_i].get('id')
    cheapest_ride = routes_details[r_i].cssselect('div.priceItem')[0].cssselect('td.detail_icon')[0]
    data['cheapest_ride_id'] = cheapest_ride.get('id')
    data['cheapest_ride_price'] = re.findall('\d+', cheapest_ride.text_content())[0]
    print data
    break



