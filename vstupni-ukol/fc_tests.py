#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os.path
import datetime

from src.CombinationsFinder import CombinationsFinder

# Filepaths
current_dir = os.path.dirname(os.path.realpath(__file__))
test_inputs_dir = os.path.abspath(current_dir+'/test_inputs')

# Test class
class TestCombinationsFinder(unittest.TestCase):
    """
    Perform tests for some important methods of CombinationsFinder class.
    Check if the found combinations are valid for the two datasets.
    Check if the connections and combinations generated for small dataset correspond to the ones manually found.
    """

    # Test if the read method handles errors correctly.

    def test_read_input_blank_field(self):
        """
        If there is a blank field on any line in the input data, raise an exception.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_blank_field.csv') as test_file:
            with self.assertRaises(ValueError) as context:
                c_finder.read_input(test_file)
            self.assertTrue(1 in context.exception)

    def test_read_input_fewer_fields(self):
        """
        If any line in the input data does not contain necessary number of fields, raise an exception.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_fewer_fields.csv') as test_file:
            with self.assertRaises(IndexError) as context:
                c_finder.read_input(test_file)
            self.assertTrue(2 in context.exception)

    def test_read_input_empty(self):
        """
        If the input data are empty (there are no values/rows), raise an exception.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_empty.csv') as test_file:
            with self.assertRaises(ValueError) as context:
                c_finder.read_input(test_file, False)
            self.assertTrue(3 in context.exception)

    def test_read_input_empty_with_header(self):
        """
        If the input data contain a header, but otherwise are empty, raise an exception.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_empty_with_header.csv') as test_file:
            with self.assertRaises(ValueError) as context:
                c_finder.read_input(test_file, True)
            self.assertTrue(3 in context.exception)

    def test_read_input_no_header_not_set(self):
        """
        If the input data have no header, but the header flag is set to True, raise an exception.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_no_header.csv') as test_file:
            with self.assertRaises(ValueError) as context:
                c_finder.read_input(test_file, True)
            self.assertTrue(4 in context.exception)

    def test_read_input_no_header(self):
        """
        Check if data file with no header is processed with no problems.
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/read_test_no_header.csv') as test_file:
            c_finder.read_input_and_get_combinations(test_file, False, 4)
            self.assertTrue('u1' in c_finder.graph_nodes)

    # Test if the generated variables from the small dataset correspond to the manually found values.

    def test_generated_connections(self):
        """
        Check if the generated connections are the same as manually found connections in the small dataset.
        """
        # Connections found manually in the data.
        manual_connections = [
            ('u2', 'h2'), ('u2', 'h3'), ('h1', 'u1'), ('d3', 'u2'),
        ]
        # Generate connections programatically.
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/small_data.csv') as test_file:
            c_finder.read_input_and_get_combinations(test_file, True, 4)
        # Compare it!
        self.assertTrue(set(manual_connections) == set(c_finder.graph_edges.keys()))

    def test_generated_combinations(self):
        """
        Check if the generated combinations are the same as manually found combinations in the small dataset.
        """
        # Combinations found manually in the data.
        manual_combinations = [
            ('d3', 'u2'), ('h1', 'u1'), ('u2', 'h2'), ('u2', 'h3'), ('d3', 'u2', 'h2'), ('d3', 'u2', 'h3'),
        ]
        # Generate combinations programatically.
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/small_data.csv') as test_file:
            c_finder.read_input_and_get_combinations(test_file, True, 4)
        # Transform lists to tuples (because list is not hashable).
        program_combinations = [tuple(x) for x in c_finder.all_paths]
        # Compare it!
        self.assertTrue(set(manual_combinations) == set(program_combinations))

    # Test validity of combinations found in the datasets.

    def test_if_found_combinations_are_valid_1(self):
        """
        Check that all combinations found in the small dataset are valid.
        (only basic check - other check are in fact used in the tested class methods).
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/small_data.csv') as test_file:
            combinations = c_finder.read_input_and_get_combinations(test_file, True, 4)
            self.assertTrue(self._check_combinations(combinations, c_finder.flight_database))

    def test_if_found_combinations_are_valid_2(self):
        """
        Check that all combinations found in the task dataset are valid.
        (only basic check - other check are in fact used in the tested class methods).
        """
        c_finder = CombinationsFinder()
        with open(test_inputs_dir + '/task_data.csv') as test_file:
            combinations = c_finder.read_input_and_get_combinations(test_file, True, 4)
            self.assertTrue(self._check_combinations(combinations, c_finder.flight_database))

    # Test the private stopover method.

    def test_stopover_wrong_date_format(self):
        """
        Check that wrong date format raises an exception.
        """
        with self.assertRaises(ValueError) as context:
            CombinationsFinder._check_two_flights_stopover('2014', '2015', 4, 1)

    def test_stopover_ok(self):
        """
        Correct stopover.
        """
        self.assertTrue(CombinationsFinder._check_two_flights_stopover('2016-10-11T10:10:00', '2016-10-11T13:10:00', 4, 1))

    def test_stopover_early(self):
        """
        The second flight takes off earlier than the minimal stopover.
        """
        self.assertFalse(CombinationsFinder._check_two_flights_stopover('2016-10-11T10:10:00', '2016-10-11T11:00:00', 4, 1))

    def test_stopover_late(self):
        """
        The second flight takes off later than the maximal stopover.
        """
        self.assertFalse(CombinationsFinder._check_two_flights_stopover('2016-10-11T10:10:00', '2016-10-11T15:00:00', 4, 1))

    def test_stopover_ok_early(self):
        """
        Edge test case for almost early take off.
        """
        self.assertTrue(CombinationsFinder._check_two_flights_stopover('2016-10-11T10:10:00', '2016-10-11T11:10:00', 4, 1))

    def test_stopover_ok_late(self):
        """
        Edge test case for almost late take off.
        """
        self.assertTrue(CombinationsFinder._check_two_flights_stopover('2016-10-11T10:10:00', '2016-10-11T14:10:00', 4, 1))

    def test_stopover_past(self):
        """
        Check that the second flight that takes off before arrival of the first flight cannot be used.
        """
        self.assertFalse(CombinationsFinder._check_two_flights_stopover('2016-10-11T18:10:00', '2016-10-11T16:30:00', 4, 1))

    # Helper methods

    def _check_combinations(self, combinations, flight_database):
        """
        Check that all flight combinations are valid.

        Args:
            combinations (list): List of flight combinations.
            flight_database (dir): Directory of flight information.

        Returns:
            True if all combinations are valid. False if at least one combination is invalid.
        """
        for comb in combinations:
            if not self.is_combination_valid(comb, flight_database):
                return False
        # All combinations are valid.
        return True

    def is_combination_valid(self, combination, flight_database):
        """
        Check that the inspected flight combination is valid.

        Args:
            combination (list): List of flight numbers (strings).
            flight_database (dir): Directory of flight information.

        Returns:
            True if the combination is valid, False otherwise.
        """
        indexes = range(0, len(combination)-1)  # Process all but last flight.
        for i in indexes:
            # Get flights information.
            flight_1 = flight_database[combination[i]]
            flight_2 = flight_database[combination[i+1]]
            # Is destination of the first flight same as the source of the second flight?
            if flight_1['destination'] != flight_2['source']:
                return False
            # Does the first flight land before the second one takes off?
            arrival_time = datetime.datetime.strptime(flight_1['arrival_time'], '%Y-%m-%dT%H:%M:%S')
            departure_time = datetime.datetime.strptime(flight_2['departure_time'], '%Y-%m-%dT%H:%M:%S')
            if arrival_time >= departure_time:
                return False
        # Everything OK
        return True


# Run all tests when the file is run from terminal.
if __name__ == '__main__':
    unittest.main()
