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

class Stretch:
    def __init__(self,dep_city,arr_city,distance,duration,route):
        self.dep_city=dep_city
        self.arr_city = arr_city
        self.distance=distance
        self.duration=duration
        self.route=route


#popultate a list with name of the city and coordinate
def populate (string):
    list = []
    for str in string:
        temp = geolocator.geocode(str,timeout=None)
        city = City(str,temp.longitude,temp.latitude)
        list.append(city)
    
    return list

def get_stretch(dep_city,arr_city):
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
    duration = res['routes'][0]['duration']/60
    route = res['routes'][0]['geometry']
    s = Stretch(dep_city,arr_city,distance,duration,route)
    return s

'''fill matrix with distances between city, only compute for lower trinagular matrix but we can assume the distance not changing much and cut in half the time soo...'''
def fill_matrix(list):
    distance_matrix = np.zeros((len(list),len(list)),Stretch)
    for x in range(len(list)):
        for y in range(x):
            distance_matrix[x][y] = get_stretch(list[x],list[y])
            distance_matrix[y][x]=distance_matrix[x][y]
    
    return distance_matrix

def distance_form_stretch(stretch_matrix):
    l = len(stretch_matrix[0])
    distance_matrix = np.zeros((l,l))
    for x in range(l):
        for y in range(l):
            if isinstance(stretch_matrix[x][y],Stretch):
                distance_matrix[x][y]=stretch_matrix[x][y].distance
            else:
                distance_matrix[x][y]=0

    return distance_matrix

def print_geometry(stretch,m):
    
    route =polyline.decode(stretch.route)

    folium.PolyLine(
        route,
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(m)

    folium.Marker(
        location=[stretch.dep_city.lat,stretch.dep_city.lon],
        icon=folium.Icon(icon='flag', color='green')
    ).add_to(m)

    folium.Marker(
        location=[stretch.arr_city.lat,stretch.arr_city.lon],
        icon=folium.Icon(icon='flag', color='green')
    ).add_to(m)

    return m

def print_map(stretch_matrix,minimum_tree):
    length = len(minimum_tree[0])
    tot_distance=0
    tot_duration =0
    m = folium.Map(location=[ 40.072666376,-102.222165778],zoom_start=5)
    for x in range(length):
        for y in range(length):
            if(minimum_tree[x][y]!=0):
                stretch=stretch_matrix[x][y]
                tot_distance+=stretch.distance
                tot_duration+=stretch.duration
                m=print_geometry(stretch,m)

    print("total duration: "+str(tot_duration/60)+"h")
    print("total distance: "+str(tot_distance)+"KM")
    m.save("map.html")


def main():
    place = ["Washington D.C.","New York","Boston","Buffalo, NY","Detroit","Chicago","San Francisco","San Jose","Los Angeles","Miami","Houston","New Orleans","Las Vegas","West Glacier, MT","Tusayan","Jackson Hole, WY","El Portal, CA"]
    err = ["Washington D.C.","New York","Boston","Buffalo"]

    start_time = time.perf_counter()
    list = populate(place)
    stretch_matrix= fill_matrix(list)
    end_time = time.perf_counter()
    
    print("time ellapsed: "+ str(end_time-start_time))

    distance_matrix=distance_form_stretch(stretch_matrix)
    
    Tcsr = minimum_spanning_tree(distance_matrix)
    minimum_tree = Tcsr.toarray()

    print_map(stretch_matrix,minimum_tree)
    

main()
