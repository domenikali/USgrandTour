from geopy.geocoders import Nominatim
import numpy as np
from numpy import savetxt
import requests
import time
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import polyline
import folium

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
def populate (string):
    list = []
    for str in string:
        temp = geolocator.geocode(str,timeout=None)
        city = City(str,temp.longitude,temp.latitude)
        list.append(city)
    
    return list

def get_distance(dep_city,arr_city):
    #print(string)
    string = dep_city.coordinate()+";"+arr_city.coordinate()
    url = 'http://router.project-osrm.org/route/v1/driving/'+string
    r = requests.get(url)
    res = r.json()
    #print(string)
    if res["code"] == "NoRoute":
        print("no route from " + str(dep_city)+" to "+ str(arr_city))
        return -1

    distance = res['routes'][0]['distance']/1000
    return round(distance)

#fill matrix with distances between city, only compute for lower trinagular matrix but we can assume the distance not changing much and cut in half the time soo...
def fill_matrix(list):
    distance_matrix = np.zeros((len(list),len(list)))
    for x in range(len(list)):
        for y in range(x):
            #string = list[x].coordinate()+";"+list[y].coordinate()
            distance_matrix[x][y] = get_distance(list[x],list[y])
    
    return np.tril(distance_matrix) + np.tril(distance_matrix, -1).T

def print_geometry(dep_city,arr_city,m):
    string = dep_city.coordinate()+";"+arr_city.coordinate()
    url = 'http://router.project-osrm.org/route/v1/driving/'+string
    r = requests.get(url)
    res = r.json()
    route =polyline.decode(res['routes'][0]['geometry'])


    folium.PolyLine(
        route,
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(m)

    folium.Marker(
        location=[dep_city.lat,dep_city.lon],
        icon=folium.Icon(icon='play', color='green')
    ).add_to(m)

    folium.Marker(
        location=[arr_city.lat,arr_city.lon],
        icon=folium.Icon(icon='stop', color='red')
    ).add_to(m)

    return m




def main():
    place = ["Washington D.C.","New York","Boston","Buffalo, NY","Detroit","Chicago","San Francisco","San Jose","Los Angeles","Miami","Houston","New Orleans","Las Vegas","West Glacier, MT","Tusayan","Jackson Hole, WY","El Portal, CA"]
    err = ["Washington D.C.","New York","Boston","Buffalo"]

    start_time = time.perf_counter()
    list = populate(place)
    distance_matrix= fill_matrix(list)
    end_time = time.perf_counter()
    
    print("time ellapsed: "+ str(end_time-start_time))
    
    Tcsr = minimum_spanning_tree(distance_matrix)
    minimum_tree = Tcsr.toarray()
    
    m = folium.Map(location=[ 40.072666376,-102.222165778],zoom_start=8)
    

    for x in range(len(list)):
        for y in range(len(list)):
            if minimum_tree[x][y]!=0:
                m=print_geometry(list[x],list[y],m)

    m.save("map.html")
    

main()