from geopy.geocoders import Nominatim
import numpy as np
import requests

geolocator = Nominatim(user_agent="test")

class City:
    def __init__(self,name,lon,lat):
        self.name=name
        self.lon=lon
        self.lat=lat
    
    def __str__(self) :
        return self.name + " " +self.coordinate()
    
    def coordinate (self) : 
        return str(self.lon)+","+str(self.lat)

#popultate a list with name of the city and coordinate
def populate (*string):
    list = []
    for str in string:
        temp = geolocator.geocode(str,timeout=None)
        city = City(str,temp.longitude,temp.latitude)
        list.append(city)
    
    return list

def get_distance(string):
    #print(string)
    url = 'http://router.project-osrm.org/route/v1/driving/'+string
    r = requests.get(url)
    res = r.json()
    #print(res['routes'][0]['distance'])
    distance = res['routes'][0]['distance']/1000
    return round(distance,1)

#fill matrix with distances between city, only compute for lower trinagular matrix but we can assume the distance not changing much and cut in half the time soo...
def fill_matrix(list):
    distance_matrix = np.zeros((len(list),len(list)))
    for x in range(len(list)):
        for y in range(x):
            string = list[x].coordinate()+";"+list[y].coordinate()
            distance_matrix[x][y] = get_distance(string)
    
    return np.tril(distance_matrix) + np.tril(distance_matrix, -1).T

    
list = populate("Bologna","Imola","Bari","Milano","Roma")

distance_matrix= fill_matrix(list)

#debug
for city in list:
    print(str(city))


print(distance_matrix)