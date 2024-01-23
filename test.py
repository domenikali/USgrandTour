import requests
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="test")

dep_city = geolocator.geocode("Bologna")
arr_city = geolocator.geocode("Imola")

url = 'http://router.project-osrm.org/route/v1/driving/'+str( dep_city.longitude) +','+ str(dep_city.latitude)+';'+str( arr_city.longitude) +','+ str(arr_city.latitude)
r = requests.get(url)
res = r.json()
distance =res['routes'][0]['distance']
duration = res['routes'][0]['duration']

print("KM: "+str(distance/1000) )
print("min: "+str(round(duration/60)))
