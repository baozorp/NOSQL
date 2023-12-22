import json
import requests
import time


def set_rooms():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_rooms').json()


def set_users():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_users').json()


def get_room_by_description(str):
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/filter?description={str}').json()


def get_by_id():
    id = '657f29abe26d9569cb709e37'
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/by_id/{id}').json()


def get_all_rooms():
    return requests.get(
        'http://127.0.0.1:8005/api/rooms/').json()


def get_all_users():
    return requests.get(
        'http://127.0.0.1:8005/api/users/').json()


def clear_rooms():
    return requests.get(
        f"http://127.0.0.1:8005/api/rooms/clear_collection?collection_name=rooms").json()


def clear_users():
    return requests.get(
        f"http://127.0.0.1:8005/api/users/clear_collection?collection_name=users").json()


# with open('data_loading/rooms.json', 'r') as jsons:
#     a = json.load(jsons)
#     print(len(a))

def set_data():
    print(clear_rooms())
    print(clear_users())
    print(set_rooms())
    print(set_users())


# # set_data()
# print(len(get_all_rooms()))
# print(len(get_all_users()))
print(len(get_room_by_description("Spain")))
# with open(f'data_loading/users.json', 'r') as rooms_json:
#     rooms = json.load(rooms_json)
# print(len(rooms))
