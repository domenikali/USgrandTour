# US Grand Tour

Using the Christofides algorithm, this project finds the shortest path between selected points in the US.
All distances will be in kilometers (KM), calculated based on the shortest driving distance by car.

---

# Method

For the API, I chose the OSMR API based on OpenStreetMap. Using the `requests` library in Python, we can send queries and retrieve the shortest driving distance between two points.

Using this API, we can populate a matrix with the distances between cities, creating a complete graph.

With the SciPy library, we can find the minimum spanning tree for the graph.

Additionally, using Folium and the API, we can create an HTML website that includes an interactive map.

# TODOs

- [X] Research APIs to retrieve distances for all points
- [X] Use the API to create a weighted connected graph
- [X] Find the minimum spanning tree
- [X] Complete the graph
- [ ] Solve using the Christofides algorithm
