import requests

part ="11.32730,44.49931"
dest = "11.4814,44.4426"
url = 'http://router.project-osrm.org/route/v1/driving/'+ part +';'+dest
r = requests.get(url)
res = r.json()
distance =res['routes'][0]['distance']
duration = res['routes'][0]['duration']

print(distance/1000 )
print(duration/60)
