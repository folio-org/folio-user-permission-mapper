import networkx as nx

from dto.models import AnalysisResult
from utils import env


def generate_graph(analysis_result: AnalysisResult):
    graph = nx.DiGraph()
    processed_nodes = set()
    processed_edge = set()
    for permission_name, sub_permissions in analysis_result.permissionPermissionSets.items():
        if permission_name.startswith("SYS#"):
            continue
        if permission_name not in processed_nodes:
            processed_nodes.add(permission_name)
            graph.add_node(permission_name)
        for sub_permission_name in sub_permissions:
            if permission_name.startswith("SYS#"):
                continue
            if sub_permission_name not in processed_nodes:
                processed_nodes.add(sub_permission_name)
                graph.add_node(sub_permission_name)
            if (permission_name, sub_permission_name) not in processed_edge:
                processed_edge.add((permission_name, sub_permission_name))
                graph.add_edge(permission_name, sub_permission_name)

    nx.write_gexf(graph, f"./.temp/{env.get_tenant_id()}/permissionSets.gexf")
