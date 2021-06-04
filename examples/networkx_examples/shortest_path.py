import networkx


class Edge:
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'


graph = networkx.Graph()
graph.add_edges_from([
    (Edge.a, Edge.b),
    (Edge.a, Edge.c),
    (Edge.c, Edge.d),
    (Edge.b, Edge.d),
])
print(networkx.shortest_path(graph, Edge.a, Edge.d))
