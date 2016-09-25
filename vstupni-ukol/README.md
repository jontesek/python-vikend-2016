# Entry task for Python weekend - flight planner

Flight planner script implemented in Python 2.7. No external modules used.

Its goal is to show (based on the input data) all possible combinations (or rather sequences) of subsequent flights (at least 2 flights) with determined stopover interval.

## Usage
The script `/find_combinations.py` reads from `stdin` and expects input string in the following format:
```
source,destination,departure,arrival,flight_number
USM,HKT,2016-10-11T10:10:00,2016-10-11T11:10:00,PV511
USM,HKT,2016-10-11T18:15:00,2016-10-11T19:15:00,PV476
```
For example, you can run the script by using a pipe like this: `cat input.csv | python find_combinations.py` (in UNIX).

The script writes to `stdout`. Sample output in CSV format:
```
source,destination,total_duration,flights_count,start_time,end_time,flights_combination
HKT,HKT,5.92,2,2016-10-11T05:15:00,2016-10-11T11:10:00,h1 u1
USM,BWN,2.52,2,2016-10-11T21:25:00,2016-10-11T23:56:00,u2 h2
```

### Parameters
You can set several parameters in script's source code (line 9 in `/find_combinations.py`) (data type, default value):
* `MAX_STOPOVER_HOURS (int, 4)`: Maximal waiting time between two subsequent flights (in hours).
* `MIN_STOPOVER_HOURS (int, 1)`: Minimal...
* `MAX_FLIGHTS_COUNT (int, 10)`: Maximal number of flights during the whole trip.
* `FORBID_BACKLINKS (boolean, False)`: If true, once visited airport cannot be visited again.
Except if the trip starts and ends in the same airport ("return trip").
* `OUTPUT_FORMAT (string, 'csv')`: Format in which the results should be printed: 'csv', 'json'.

### Errors
The script might terminate during reading the input if any line in the input triggers any of the following conditions:
* The line contains no commas.
* The line contains less than 5 fields.
* The line contains an empty field.

In this case, an error message (containing also number of the problematic line) is printed to `stderr`.

## Technical solution
This section briefly explains how the search for consequent flights is performed.

The solution is based on graph theory. The graph consists of:
* nodes - individual flights. They are labeled just by flight number.
* edges - possible connections of the flights. An edge between two flights means that the passanger can, after landing at the airport, continue with the second flight from this airport and he will not wait more than X hours.

After the graph is created, all paths (combinations, trips) in the graph are found. A path can contain a certain node (flight) only once.
Looking for the paths is done using a recursive depth-first search (without labelling).

During the search, certain conditions are being checked to ensure that the created path is valid.
The most important one is that the trip must not contain two same segments. A segment is a certain route (from one airport to another one) on which you can fly only once during the trip.
Note: the trip may start and terminate at the same airport.

To better demonstrate the solution, I made two images showing a graph created from a small sample data file (`/test_inputs/small_data.csv`).
They are located in the `/info` folder of this repository:
* `graph_actual.jpg` shows the used graph. Green lines (4 in total) are edges actually present in the graph (the red-crossed line is not there). They represent the connections which are possible.
Black lines represent connections which were evaluated whether they are possible or not. For clarity, some black lines are omitted (from D2, H1, H3).
* `graph_top-level.jpg` shows a top-level look on the used graph - showing airports as nodes and flights as edges.

### Basic data structures
The following important instance variables are used in the main class (`src/CombinationsFinder.py`):
* `self.flight_database = {}` ... Information about flights. `'flight_number' => {'source': 'XYZ',...}`
* `self.airport_flights = {}` ... Flights from given airport. `'airport_code' => ['fl1', 'fl4', ...]`
* `self.graph_nodes = {}` ... Flights. `'flight_number' => None`
* `self.graph_edges = {}` ... Possible connections of flights. `('flight_1', 'flight_2) => None`
* `self.all_paths = []` ... Found paths (combinations) in the graph. `[['fl1', 'fl2'], ['fl4', 'fl7', 'fl2']]`

## Tests
Tests can be performed by running `/fc_tests.py`.

A test class (`TestCombinationsFinder`) tests class `src.CombinationsFinder` - its public methods and a private method for stopover check.
Also validity of found combinations is checked and manually created connections and combinations from the small dataset are compared to the generated ones.
Both normal operation and exceptional states are tested.
Files from `/test_inputs` directory are used as the input data.