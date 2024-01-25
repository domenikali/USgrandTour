# US grand tour

Using the Christofides algorithm find the shortest path between selected points in the US
All distances will be in KM, and it will count the short distance by car.

---

# Method

For the api I chose the OSMR API based on Opne Street Map, using the 'request' library in python is possible to recive the query and know the shortest driving distance between two points

Using this API we can fill a matrix with the distance of the city between each other creating a complete graph

Using the SciPy library we can find the minimum spanning tree

Using the same API and folium we can create a html website with the map inside

# TODOs

- [X] research APIs to have distance for all points
- [X] using this API to create a wheighted connected graph
- [X] find the shortest spanning tree
- [ ] Complete the graph
- [ ] solve using the Christofides algorithm
