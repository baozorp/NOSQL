import json
import requests


def set_rooms():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_rooms').json()


def set_users():
    return requests.get(
        f'http://127.0.0.1:8005/api/data_loader/load_users').json()


def get_by_description():
    string = 'sea'
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/filter?name={string}').json()


def get_by_id():
    id = '657f29abe26d9569cb709e37'
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/by_id/{id}').json()


def get_all():
    return requests.get(
        'http://127.0.0.1:8005/api/rooms/').json()


def clear_all():
    return requests.get(
        f"http://127.0.0.1:8005/api/rooms/clear_collection?collection_name=rooms").json()


# with open('data_loading/rooms.json', 'r') as jsons:
#     a = json.load(jsons)
#     print(len(a))
# print(clear_all())
print(set_users())
