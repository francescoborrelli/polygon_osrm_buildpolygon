#  Copyright (c) 2020. AV Connect Inc.
import requests
import json

HOST = 'http://localhost:5000'

response = requests.post( HOST + "/auth",
                         data=json.dumps({"username": "bwootton", "password": "avconnect"}),
                         headers={"Content-Type": "application/json"})

token = response.json()
print(token)

# response = requests.get("http://localhost:5000/secret")
# print(response)
#
# response = requests.get("http://localhost:5000/drivers", headers={"Authorization": "Bearer " + token["access_token"]})
# print(response.json())

response = requests.get(HOST + "/charge_stations",
                         params={'waypoints':'37.733223, -122.244648;37.802735, -122.266164'},
                         headers={"Authorization": "Bearer " + token["access_token"],
                                  "Content-Type": "application/json"})
print(response.status_code)
print(response.json())
# response = requests.post(HOST + "/drive",
#                          data=json.dumps({'driver_name': 'Bruce Wootton', 'vehicle_name': 'Grey_Kona'}),
#                          headers={"Authorization": "Bearer " + token["access_token"],
#                                   "Content-Type": "application/json"})
# print(response.status_code)


# if response.status_code == 200:
#     print(response.json())
#
# response = requests.post("http://localhost:5000/vehicles",
#                          data=json.dumps({'vehicles': ['Green Kona', 'Blue Nexo']}),
#                          headers={"Authorization": "Bearer " + token["access_token"],
#                                   "Content-Type": "application/json"})
#
# print(response.status_code)
# if response.status_code == 200:
#     print(response.json())