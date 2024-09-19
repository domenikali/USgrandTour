from geopy.geocoders import Nominatim
import numpy as np
from numpy import savetxt
import requests
import time
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import polyline
import folium
import operator
from itertools import combinations

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

#return a stretch object by calling the OSRM api
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

#return a matrix of distance based on the full stretch matrix
def distance_form_stretch(stretch_matrix):
    l = len(stretch_matrix[0])
    distance_matrix = np.zeros((l,l))

    for (x,y),el in np.ndenumerate(stretch_matrix):
        if isinstance(el,Stretch):
            distance_matrix[x][y]=el.distance
        else:
            distance_matrix[x][y]=0

    return distance_matrix

#print a single rout in a folium map
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

#print the rout map based on a adjacent matrix
def print_map(stretch_matrix,minimum_tree):
    length = len(minimum_tree[0])
    tot_distance=0
    tot_duration =0
    m = folium.Map(location=[ 40.072666376,-102.222165778],zoom_start=5)

    for (x,y),el in np.ndenumerate(minimum_tree):
        if (el!=0):
            stretch=stretch_matrix[x][y]
            tot_distance+=stretch.distance
            tot_duration+=stretch.duration
            m=print_geometry(stretch,m)

    print("total duration: "+str(tot_duration/60)+"h")
    print("total distance: "+str(tot_distance)+"KM")
    m.save("map.html")

#compute the odd verticis of the minimum spanning tree
def compute_odd_vert(minimum_tree,list):
    odd_vert = []

    #for (x,y),el in np.ndenumerate(minimum_tree):
    
    for i in range(len(minimum_tree)):
        count =0
        for j in range(len(minimum_tree)):
            if i!=j:
                if minimum_tree[i][j]!=0:
                    count+=1
                if minimum_tree[j][i]!=0:
                    count+=1
        if count %2!=0:
            odd_vert.append(list[i])

    return odd_vert

#eliminate all non perfect matching from the combination
def clean_list(altro):
    t=[]
    for x in altro:
        
        temp=[]
        for (a,b) in x:
            temp.append(a)
            temp.append(b)
        if len(set(temp))==len(x)*2:
            t.append(x)
    return t

#return the total distance of the matching
def get_distance(s,stretch_matrix,city_list):
    distance =0
    for (x,y) in s:
        x_index = city_list.index(x)
        y_index = city_list.index(y)
        distance+=stretch_matrix[x_index][y_index].distance
    return distance

# return the minimum weight perfect matching for the matrix based on distance 
def perfect_matching(matching_list,stretch_matrix,city_list):
    km = get_distance(matching_list[0],stretch_matrix,city_list)
    shortest = matching_list[0]
    for x in matching_list:
        temp=get_distance(x,stretch_matrix,city_list)
        if temp<km:
            km=temp
            shortest=x
    return shortest

#add perfect matching into the minimum spanning tree
def add_matching(minimum_tree,matching,city_list):
    for (x,y) in matching:
        x_index = city_list.index(x)
        y_index = city_list.index(y)
        minimum_tree[x_index][y_index]=1

    return minimum_tree

def main():
    #places to visit
    place = ["Washington D.C.","New York","Boston","Buffalo, NY","Detroit","Chicago","San Francisco","San Jose","Los Angeles","Miami","Houston","New Orleans","Las Vegas","West Glacier, MT","Tusayan","Jackson Hole, WY","El Portal, CA","Seattle"]
    err = ["Washington D.C.","New York","Boston","Richmond"]

    #calculating route for each place to each other and form a complete graph
    start_time = time.perf_counter()
    city_list = populate(place)
    stretch_matrix= fill_matrix(city_list)
    end_time = time.perf_counter()
    print("time ellapsed during requests: "+ str(end_time-start_time))

    #find a minimum spanning tree using distance as primary selector
    distance_matrix=distance_form_stretch(stretch_matrix)
    Tcsr = minimum_spanning_tree(distance_matrix)
    minimum_tree = Tcsr.toarray()

    #minimum weight perfect matching brute force
    odd_verticis = compute_odd_vert(minimum_tree,city_list)
    res = list(combinations(odd_verticis,2))
    matching_list = set(list(combinations(res,int(len(odd_verticis)/2))))
    matching_list = clean_list(matching_list)
    matching = perfect_matching(matching_list,stretch_matrix,city_list)

    #debug and map printing  
    print("added distance: ",get_distance(matching,stretch_matrix,city_list))
    minimum_tree = add_matching(minimum_tree,matching,city_list)
    print_map(stretch_matrix,minimum_tree)
    start_time = time.perf_counter()
    print("time ellapsed during algo: "+ str(start_time-end_time))
    
if __name__ =="__main__":
    main()
