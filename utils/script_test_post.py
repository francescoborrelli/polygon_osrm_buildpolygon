#  Copyright (c) 2020. AV Connect Inc.
import utils.jwt_client as jwc
from datetime import datetime, timedelta
import pytz
import json


def dt_to_sec(dt):
    return int((dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())

client = jwc.JWTClient("http://localhost:5000", "bwootton", "avconnect")
# time = datetime.now().astimezone(pytz.utc) - timedelta(seconds=10)
# time_array = [time + timedelta(seconds=t) for t in range(10)]
# ns_time_array = [dt_to_sec(t)*1000*1000*1000 for t in time_array]
# awesome_array = [list(a) for a in zip(ns_time_array, range(10))]
# radical_array = [list(a) for a in zip(ns_time_array, [i*2.0 for i in range(10)])]
# print("FU")
# data = {
#     'vehicle_name': 'brucemobile',
#     'data': {
#         'awesome': awesome_array,
#         'radical': radical_array
#     }
# }
# print(data)
# response = client.json_post("/can_data", json.dumps(data))
response = client.get("/latest_soc?vehicle_name=White_Niro2")
print(response)
