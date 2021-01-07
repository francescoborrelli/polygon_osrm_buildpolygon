import requests

raw_addr1 = '77.857151,20.607105'
raw_addr2 =  '77.941062,20.676537'
raw_addr1 = '122.4194,37.7749'
raw_addr2 = '118.2437,34.0522'
server_ip  = '34.220.117.47'
server_ip  = '127.0.0.1'

def get_route(lat1, lat2, lon1, lon2):
    raw_addr1 = "{},{}".format(lon1,lat1)
    raw_addr2 = "{},{}".format(lon2, lat2)
    print(raw_addr1)
    print(raw_addr2)
    # Get matches
    response = requests.get("http://{}:5000/nearest/v1/driving/{}?number=1".format(server_ip, raw_addr1))
    print(response.json()['waypoints'][0]['location'])
    addr1 = response.json()['waypoints'][0]['location']
    addr1_str = "{},{}".format(addr1[0],addr1[1])

    response = requests.get("http://{}:5000/nearest/v1/driving/{}?number=1".format(server_ip, raw_addr2))
    print(response.json()['waypoints'][0]['location'])
    addr2 = response.json()['waypoints'][0]['location']
    addr2_str = "{},{}".format(addr2[0],addr2[1])

    # get route
    response = requests.get("http://{}:5000/route/v1/driving/{};{}?steps=true".format(server_ip, addr1_str, addr2_str))
    # response = requests.get("http://{}:5000/route/v1/driving/{};{}?steps=true".format(server_ip, raw_addr1, raw_addr2))

    # print(response.json())
    print("received")
    return response

import functools
def get_table(slat, slon, dlatlist, dlonlist):
    sstring = "{},{}".format(slon, slat)
    astring = functools.reduce(lambda x,y: x+";{},{}".format(dlonlist[y],dlatlist[y]), range(len(dlatlist)),sstring)
    url = "http://{}:5000/table/v1/driving/{}?sources=0&annotations=distance,duration".format(server_ip, astring)
    response = requests.get(url)
    return response.json()