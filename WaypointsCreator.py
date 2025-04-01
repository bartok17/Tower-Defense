import json


'''tutaj można tworzyć tablice dróg dla jednostek
stwórz listy i użyj save_lists_to_json() aby skompilować'''

def save_lists_to_json(filename, **lists):

    with open(filename, 'w') as f:
        json.dump(lists, f)

def load_lists_from_json(filename):

    with open(filename, 'r') as f:
        return json.load(f)


mapName = "map1"

list1 = [(725,0),(725,585),(415,585),(0,1000)]
list2 = [(725,0),(725,585),(970,1000)]


# Save waypoints to JSON
save_lists_to_json( mapName + "_waypoints.json", road1=list1, road2=list2)

loaded_lists = load_lists_from_json(mapName + "_waypoints.json")
print(loaded_lists)
