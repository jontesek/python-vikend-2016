#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

from src.CombinationsFinder import CombinationsFinder

# Parameters
MAX_STOPOVER_HOURS = 4
MIN_STOPOVER_HOURS = 1
MAX_FLIGHTS_COUNT = 10
FORBID_BACKLINKS = False
OUTPUT_FORMAT = 'csv'

# Create the main object.
comb_finder = CombinationsFinder()

# 1. Read flight data from standard input.
# Format: source,destination,departure,arrival,flight_number
try:
    comb_finder.read_input(sys.stdin)
except Exception, e:
    sys.exit(e[0])

# 2. Find subsequent flights.
comb_finder.generate_possible_connections(MAX_STOPOVER_HOURS, MIN_STOPOVER_HOURS)

# 3. Find all flight combinations.
all_combinations = comb_finder.find_flight_combinations(MAX_FLIGHTS_COUNT, FORBID_BACKLINKS)

# 4. Show the result.
if OUTPUT_FORMAT == 'csv':
    print(comb_finder.process_and_format_found_combinations_to_csv(all_combinations))
elif OUTPUT_FORMAT == 'json':
    print(comb_finder.process_and_format_found_combinations_to_json(all_combinations))
else:
    sys.exit('Please specify a supported output format.')
