from datetime import datetime, timedelta
import requests
import random

from yaml import load_all


def set_rooms():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_rooms').json()


def set_users():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_users').json()


def set_all():
    return requests.get(
        f"http://127.0.0.1:8005/api/data_loader/load_all").json()


def get_room_by_description(str):
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/filter_by_description?description={str}').json()


def get_room_by_location(str):
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/filter_by_location?host_location={str}').json()


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


def get_all_reservations():
    return requests.get(
        'http://127.0.0.1:8005/api/reservations/').json()


def clear_rooms():
    return requests.get(
        f"http://127.0.0.1:8005/api/rooms/clear_collection?collection_name=rooms").json()


def clear_users():
    return requests.get(
        f"http://127.0.0.1:8005/api/users/clear_collection?collection_name=users").json()


def clear_reservations():
    return requests.get(
        f"http://127.0.0.1:8005/api/reservations/clear_collection?collection_name=reservations").json()


def find_by_date():
    return requests.get(
        f'http://127.0.0.1:8005/api/reservations/find_by_date?in_date=20020509&out_date=20020516').json()


def clear_data():
    print(clear_rooms())
    print(clear_users())
    print(clear_reservations())


def set_data():
    print(set_rooms())
    print(set_users())


# clear_data()
print(set_all())
# set_rooms()

# print(len(get_all_rooms()))
# print(len(get_all_users()))
# print(len(get_all_reservations()))
# print(find_by_date())
# print(len(get_room_by_description("Spain")))
# print(len(get_room_by_location("Spain")))
# with open(f'data_loading/users.json', 'r') as rooms_json:
#     rooms = json.load(rooms_json)
# print(len(rooms))
