from itertools import count
import requests


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


def get_by_id(id: str):
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/find_by_id?id={id}').json()


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


def find_by_date(current_date: int, in_date: int, out_date: int):
    return requests.get(
        f'http://127.0.0.1:8005/api/reservations/find_by_date?current_date={str(current_date)}&in_date={str(in_date)}&out_date={str(out_date)}').json()


def add_reservation(reservation: dict):

    return requests.put(
        f'http://127.0.0.1:8005/api/reservations/add_reservation', json=reservation).json()


def clear_data():
    print(clear_rooms())
    print(clear_users())
    print(clear_reservations())


def set_data():
    print(set_rooms())
    print(set_users())


# clear_data()
# print(set_all())
# print(get_by_id(get_all_rooms()[0]['id']))
print(len(get_all_rooms()))
# print(len(get_all_users()))
# print(len(get_all_reservations()))
# print(len(find_by_date()))
# print(len(get_room_by_description("Spain")))
# print(len(get_room_by_location("Spain")))
# with open(f'data_loading/users.json', 'r') as rooms_json:
#     rooms = json.load(rooms_json)
# print(len(rooms))

# print(add_reservation(
#     reservation={
#         'user_id': '6585e8bacc0862a78c8f184c',
#         'room_id': get_all_rooms()[0]['id'],
#         'in_date': 20251115,
#         'out_date': 20251205,
#         'isPaid': True
#     }
# ))


# a = find_by_date(current_date=24000000, in_date=25000000, out_date=20290000)
# print(len(a))
# print(len(a))
# count = 0
# for i in a:
#     if i['room_id'] == 20150620:
#         count += 1

# # print(count)
# all = set(get_all_rooms())
