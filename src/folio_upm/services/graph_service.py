import networkx as nx

from folio_upm.dto.models import AnalysisResult
from folio_upm.utils import env


def generate_graph(analysis_result: AnalysisResult, ts=None, store: bool = False) -> nx.DiGraph:
    graph = nx.DiGraph()
    user_permission_sets = analysis_result.usersPermissionSets
    uq_user_ids = set()
    uq_permission_set_ids = set()
    for user_id, up_holder in user_permission_sets.items():
        permission_set_ids = up_holder.mutablePermissions
        if user_id not in uq_permission_set_ids:
            uq_user_ids.add(user_id)
            graph.add_node(user_id, t="user")
        for permission_set_id in permission_set_ids:
            if permission_set_id not in uq_permission_set_ids:
                graph.add_node(permission_set_id, t="ps")
                uq_permission_set_ids.add(permission_set_id)
            graph.add_edge(user_id, permission_set_id, t="user-ps")

    if store:
        nx.write_gexf(graph, f"./.temp/{env.get_tenant_id()}/permissionSets-{ts}.gexf")

    return graph
