# -*- coding: UTF-8 -*-
import datetime
import json
from collections import OrderedDict


class CombinationsFinder(object):
    """
    Main class for finding combinations of flights. There are two ways how to use this class:
    a) Use an "all-in-one" method read_input_and_get_combinations().
    b) Call the methods one by one, in the following order:
    1. read_input()
    2. generate_possible_connections()
    3. find_flight_combinations()
    At the end, to show the results, you must call process_and_format_found_paths_to_json or csv.
    """

    def __init__(self):
        """
        Define basic data structures.
        """
        self.flight_database = {}  # Information about flights. 'flight_number' => {'source': 'XYZ',...}
        self.airport_flights = {}  # Flights from given airport. 'airport_code' => ['fl1', 'fl4', ...]
        self.graph_nodes = {}      # Flights. 'flight_number' => None
        self.graph_edges = {}      # Possible connections of flights. ('flight_1', 'flight_2) => None
        self.all_paths = []        # Found paths in the graph. [['fl1', 'fl2'], ['fl4', 'fl7', 'fl2']]


    #### PUBLIC METHODS

    def read_input(self, input_data_iterator, has_header=True):
        """
        Parse the input data and populate the data structures.

        Args:
            input_data_iterator (file): File object (i.e. standard input or file iterator) containing the input text data.
                Line format: source,destination,departure,arrival,flight_number
            has_header (bool, optional): If true, the first line of the input data, containing header, is skipped.

        Raises:
            ValueError: There is a blank field on line X. | The input data are empty.
            IndexError: Input data do not contain necessary number of fields (line X).
        """
        # If set, skip header line.
        if has_header:
            header_line = input_data_iterator.readline()
            n_line = 1
            if header_line.split(',')[0].strip() != 'source':
                raise ValueError('Input data should have a header, but no header was found.', 4)
        else:
            n_line = 0
        # Parse the data and populate the structures.
        for line_flight in input_data_iterator:
            n_line += 1  # increment line number
            try:
                flight = line_flight.split(',')
                # Check if any of the fields is empty. If yes, raise an exception.
                for f_value in flight:
                    if not f_value.strip():
                        raise ValueError("There is a blank field on line %d." % n_line, 1)
                # Flight database
                f_number = flight[4].strip()    # flight number
                s_code = flight[0].strip()      # source airport code
                d_code = flight[1].strip()      # destination airport code
                self.flight_database[f_number] = {
                    'source': s_code, 'destination': d_code,
                    'departure_time': flight[2].strip(), 'arrival_time': flight[3].strip(),
                }
                # Airport database
                if s_code in self.airport_flights:   # If the code exists, add the flight to it.
                    self.airport_flights[s_code].append(f_number)
                else:                                # If the code doesn't exist, add it to the DB.
                    self.airport_flights[s_code] = [f_number]
                # If destination code is not in the database, add it.
                if d_code not in self.airport_flights:
                    self.airport_flights[d_code] = []
                # Graph nodes
                self.graph_nodes[f_number] = None
            except IndexError:
                raise IndexError("Input data do not contain necessary number of fields (line %d)." % n_line, 2)
        # Check if the data were not empty.
        if len(self.flight_database) == 0:
            raise ValueError("Input data are empty.", 3)

    def generate_possible_connections(self, max_stopover_hours, min_stopover_hours=1):
        """
        For every flight, check possible subsequent flights from the destination of this flight.

        Args:
            max_stopover_hours (int): Maximal waiting time between two subsequent flights (in hours).
            min_stopover_hours (int, optional): Minimal waiting time between two subsequent flights (in hours).
        """
        for flight_id in self.graph_nodes:
            #print("===Checking connections for flight %s from %s to %s===") % \
            #     (flight_id, self.flight_database[flight_id]['source'], self.flight_database[flight_id]['destination'])
            subsequent_flights = self.airport_flights[self.flight_database[flight_id]['destination']]
            for next_flight_id in subsequent_flights:
                if self._check_two_flights_stopover(self.flight_database[flight_id]['arrival_time'],
                                                    self.flight_database[next_flight_id]['departure_time'],
                                                    max_stopover_hours, min_stopover_hours):
                    # Add a valid connection to the graph.
                    #print next_flight_id
                    self.graph_edges[(flight_id, next_flight_id)] = None
        # OK

    def find_flight_combinations(self, max_flights_count=10, forbid_backlinks=False):
        """
        For every flight, find all paths to other flights in the graph (path = combination of flights).

        Args:
            max_flights_count (int, optional): Maximal number of flights during the whole trip.
            forbid_backlinks (bool, optional): If true, once visited airport cannot be visited again.
                Except if the trip starts and ends in the same airport ("return trip").

        Returns:
            List of all found flight combinations. I.e. [['fl1', 'fl2'], ['fl4', 'fl7', 'fl2']]
        """
        for flight_id_from in self.graph_nodes:
            #print("===Finding path from flight %s==") % flight_id_from
            init_path = [flight_id_from]
            self._find_all_paths_recursively(init_path, max_flights_count, forbid_backlinks)
        # Result
        return self.all_paths

    def read_input_and_get_combinations(self, input_data_iterator, has_header, max_stopover_hours,
                                        min_stopover_hours=1, max_flights_count=10, forbid_backlinks=False):
        """
        Total method for reading input and getting all flight combinations.
        For parameters description please see individual methods.
        """
        self.read_input(input_data_iterator, has_header)
        self.generate_possible_connections(max_stopover_hours, min_stopover_hours)
        return self.find_flight_combinations(max_flights_count, forbid_backlinks)


    #### PRIVATE METHODS

    def _get_children(self, examined_node):
        """
        Find all subsequent flights for the examined flight. (Find all children of the examined node in the graph.)

        Args:
            examined_node (str): Flight for which to search subsequent flights.

        Returns:
            List of possible flights (flight number as string).
        """
        return [flight_2 for (flight_1, flight_2) in self.graph_edges.keys() if flight_1 == examined_node]

    def _find_all_paths_recursively(self, current_path, max_flights_count=10, forbid_backlinks=False):
        """
        A recursive method for searching the graph and getting all possible paths in the graph.
        It uses a "dumb" depth-first search without labelling.
        The method gets the last node in the path and inspects all its children.
            - If the child does not violate any conditions, it is added to the path and its children are inspected, and so on.
            - If the child violates a condition, it is not added to the path and its children are not inspected.
              The script then continues by executing the next method saved in the stack.

        Args:
            current_path (list): Flights on the path so far.
            max_flights_count (int, optional): Maximal number of flights in the path.
                This might be useful when searching a graph with huge number of nodes to limit the execution time of the method.
            forbid_backlinks (bool, optional): If true, once visited airport cannot be visited again (except for cycles).

        Returns:
            False if the recursion must be stopped in the current branch.
            None if everything is OK (we can continue in the current branch).
        """
        # Check if the path is not too long.
        if len(current_path) >= max_flights_count:
            return False
        last_node = current_path[-1]
        for child in self._get_children(last_node):
            # I cannot fly with the same flight twice. It should not be possible, but just to be safe :).
            if child in current_path:
                return False
            # We must check for repeated segments.
            if self._is_segment_duplicate_in_path(current_path, child):
                return False
            # If set, I cannot return to the airport I have been to before (hovewer cycles are allowed).
            if forbid_backlinks and self._is_destination_duplicate_in_path(current_path, self.flight_database[child]['destination']):
                return False
            else:
                self.all_paths.append(current_path + [child])
                self._find_all_paths_recursively(current_path + [child], max_flights_count, forbid_backlinks)

    @staticmethod
    def _check_two_flights_stopover(arrival_str, departure_str, max_stopover_hours, min_stopover_hours):
        """
        Check two things:
            1. If the first flight may actually be connected with the second flight (based on arrival and departure times).
            1. If the waiting time between the two flights (a duration of the stopover) is in the desired interval.

        Args:
            arrival_str (str): Arrival time of the first flight in YYYY-MM-DDTHH:MM:SS format.
            departure_str (str): Departure time of the second flight in YYYY-MM-DDTHH:MM:SS format.
            max_stopover_hours (int): Maximal waiting time between two subsequent flights (in hours).
            min_stopover_hours (int): Minimal waiting time between two subsequent flights (in hours).

        Returns:
            True if the flights may be connected and the waiting time is in the interval.
            False if any of the two above mentioned conditions are not met.

        Raises:
            ValueError: Time string has a wrong format.
        """
        arrival_time = datetime.datetime.strptime(arrival_str, '%Y-%m-%dT%H:%M:%S')
        departure_time = datetime.datetime.strptime(departure_str, '%Y-%m-%dT%H:%M:%S')
        max_next_departure = arrival_time + datetime.timedelta(hours=max_stopover_hours)
        min_next_departure = arrival_time + datetime.timedelta(hours=min_stopover_hours)
        #print arrival_time, departure_time, min_next_departure, max_next_departure
        if departure_time >= min_next_departure and departure_time <= max_next_departure:
            return True
        else:
            return False

    def _is_segment_duplicate_in_path(self, path, new_flight):
        """
        Check if the flight segment (source and destination of the flight) is already present in the path.

        Args:
            path (list): List of flight numbers (strings).
            new_flight(str): Flight number to be inspected.

        Returns:
            True if the segment is in the path (the flight cannot be added to the path).
            Else if it is not (the flight can be added to the path).
        """
        # Construct path segments.
        path_segments = []
        for flight in path:
            path_segments.append((self.flight_database[flight]['source'], self.flight_database[flight]['destination']))
        # Check the new flight segment.
        new_flight_segment = (self.flight_database[new_flight]['source'], self.flight_database[new_flight]['destination'])
        if new_flight_segment in path_segments:
            return True
        # everything OK
        return False

    def _is_destination_duplicate_in_path(self, path, new_destination):
        """
        Check if the destination of the new flight is already present in the path. Hovewer, cycles (A->B->A) are allowed.
        Note: Using this method is optional.

        Args:
            path (list): List of flight numbers (strings).
            new_destination (str): Airport code.

        Returns:
            True if the the new destination is in the path (the flight cannot be added to the path).
            False if not or if the path would create a cycle (the flight can be added to the path).
        """
        # Cycles are allowed.
        if new_destination == self.flight_database[path[0]]['source']:
            return False
        # Other "intermediate" backlinks are not allowed.
        for flight_id in path:
            if new_destination == self.flight_database[flight_id]['destination']:
                return True
        # Everything OK
        return False


    #### OUTPUT methods

    def process_and_format_found_combinations_to_json(self, input_comb_list):
        """
        Process and format found flight combinations to JSON.

        Args:
            input_comb_list (list): List of combinations (paths).

        Returns:
            JSON string - list of dictionaries (each dictionary is a flight combination).
            Example:
            [
                {
                    "source": "HKT",
                    "destination": "HKT",
                    "total_duration": 5.92,             # in hours
                    "flights_count": 2,
                    "start_time": "2016-10-11T05:15:00",
                    "end_time": "2016-10-11T11:10:00",
                    "flights_sequence": ["h1", "u1"]    # the most important part :)
                },
                ...
            ]
        """
        output_list = []
        for path in input_comb_list:
            # Calculate total trip time.
            start_time = datetime.datetime.strptime(self.flight_database[path[0]]['departure_time'], '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.datetime.strptime(self.flight_database[path[-1]]['arrival_time'], '%Y-%m-%dT%H:%M:%S')
            total_duration = round((end_time - start_time).total_seconds() / 3600, 2)
            # Prepare data.
            temp_dict = OrderedDict([
                ('source', self.flight_database[path[0]]['source']),
                ('destination', self.flight_database[path[-1]]['destination']),
                ('total_duration', total_duration),
                ('flights_count', len(path)),
                ('start_time', self.flight_database[path[0]]['departure_time']),
                ('end_time', self.flight_database[path[-1]]['arrival_time']),
                ('flights_combination', path),
            ])
            # Save data.
            output_list.append(temp_dict)
        # Convert the list to JSON.
        return json.dumps(output_list)

    def process_and_format_found_combinations_to_csv(self, input_comb_list, write_header=True):
        """
        Process and format found flight combinations to CSV.

        Args:
            input_comb_list (list): List of combinations (paths).
            write_header (bool, optional): If true, the header is written on the first line of the output.

        Returns:
            CSV string - one line for one flight combination.
            Example:
                source,destination,total_duration,flights_count,start_time,end_time,flights_sequence
                HKT,HKT,5.92,2,2016-10-11T05:15:00,2016-10-11T11:10:00,h1 u1
                ...
        """
        #print('Total paths: %d') % len(input_comb_list)
        header = 'source,destination,total_duration,flights_count,start_time,end_time,flights_combination'
        output_string = header+'\n' if write_header else ''
        for path in input_comb_list:
            # Calculate total trip time.
            start_time = datetime.datetime.strptime(self.flight_database[path[0]]['departure_time'], '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.datetime.strptime(self.flight_database[path[-1]]['arrival_time'], '%Y-%m-%dT%H:%M:%S')
            total_duration = round((end_time - start_time).total_seconds() / 3600, 2)
            # Prepare data.
            temp_list = ([
                self.flight_database[path[0]]['source'],
                self.flight_database[path[-1]]['destination'],
                str(total_duration),
                str(len(path)),
                self.flight_database[path[0]]['departure_time'],
                self.flight_database[path[-1]]['arrival_time'],
                ' '.join(path),
            ])
            # Create a comma-separated string from the list. Add it to the total string.
            temp_str = ','.join(temp_list)
            output_string += temp_str + '\n'
        # Result
        return output_string
