import json

from flask import Flask
from flask import request

from src.RidesGetter import RidesGetter

# Config
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

redis_config = json.load(open('../configs/redis.json'))
r_getter = RidesGetter(redis_config, True)


# Search method
@app.route("/search")
def search():
    input_data = {
        'from': request.args.get("city_from", "all"),
        'to': request.args.get("city_to", "all"),
        'departure': request.args.get("date", '2017-01-01')
    }
    parsed_input = r_getter.parse_input(json.dumps(input_data))
    rides = r_getter.get_rides(parsed_input['from'], parsed_input['to'], parsed_input['departure'], parsed_input)
    return rides

