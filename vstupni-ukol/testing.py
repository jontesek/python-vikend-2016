
from src.CombinationsFinder import CombinationsFinder


cf = CombinationsFinder()

input_data = open('test_inputs/small_data.csv')

cf.read_input(input_data, True)
cf.generate_possible_connections(4)

print "==Nodes: ", cf.graph_nodes
print "==Edges: ", cf.graph_edges

print ">>Paths: ", cf.find_flight_combinations(10, False)

print cf.process_and_format_found_combinations_to_csv(cf.all_paths)

#print cf.airport_flights

