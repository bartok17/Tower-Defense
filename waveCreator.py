"""Script to create waves and import them to json"""
import json


def load_waves_from_json(filename):

    with open(filename, 'r') as f:
        return json.load(f)



dane = [
    {"P_time": 30, "units": [[1,3],[2,2]], "mode": 1},
    {"P_time": 10, "units": [[1,5],[2,5]], "mode": 1},
    {"P_time": 10, "units": [[1,15],[2,10]], "mode": 1}
]

# Zapis do pliku JSON
with open("Waves.json", "w",) as f:
    json.dump(dane, f)