import _pydotreader

def convert_networkx_digraph_to_graphviz_digraph(g):
    from graphviz import Digraph as GraphvizDigraph
    graph = GraphvizDigraph()
    for node in g.nodes_iter(data=True):
        attrs = node[1]
        graph.node(node[0],**attrs)

    for edge in g.edges_iter(data=True):
        graph.edge(edge[0],edge[1],**(edge[2]))
    return(graph)

def load_pygraph_digraph_from_dot(path):
    g = _pydotreader.readdot(path)
    from pygraph.classes.digraph import digraph
    graph = digraph()

    for i in range(len(g[0])):
        graph.add_node(g[0][i],attrs=g[1][i])

    for i in range(len(g[2])):
        graph.add_edge((g[2][i][0],g[2][i][1]),attrs=g[3][i])

    return(graph)

def load_graphviz_digraph_from_dot(path):
    g = _pydotreader.readdot(path)
    from graphviz import Digraph
    graph = Digraph()
    for i in range(len(g[0])):
        attr_dict = {strip_quotes(k): strip_quotes(v) for (k,v) in g[1][i]}
        graph.node(g[0][i],**attr_dict)

    for i in range(len(g[2])):
        attr_dict = {strip_quotes(k): strip_quotes(v) for (k,v) in g[3][i]}
        graph.edge(g[2][i][0],g[2][i][1],**attr_dict)

    return(graph)

def strip_quotes(string):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return(string)

def load_networkx_digraph_from_dot(path):
    g = _pydotreader.readdot(path)
    print(g)
    from networkx import DiGraph
    graph = DiGraph()

    for i in range(len(g[0])):
        attr_dict = {strip_quotes(k): strip_quotes(v) for (k,v) in g[1][i]}
        graph.add_node(g[0][i],attr_dict=attr_dict)

    for i in range(len(g[2])):
        attr_dict = {strip_quotes(k): strip_quotes(v) for (k,v) in g[3][i]}
        graph.add_edge(g[2][i][0],g[2][i][1],attr_dict=attr_dict)

    return(graph)
