"""
Graph Builder for Cytoscape.js visualization.
Generates nodes and edges for:
1. Resource Allocation Graph (RAG)
2. Wait-For Graph (WFG)
3. Deadlock Cycle highlighting
"""
from typing import Dict, List, Any
from algorithms.wait_for_graph import WaitForGraph

class GraphBuilder:
    @staticmethod
    def build_rag(
        processes: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        allocation: Dict[str, Dict[str, int]],
        request: Dict[str, Dict[str, int]],
        deadlocked_pids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Builds Cytoscape.js elements for the Resource Allocation Graph (RAG).
        Processes: circles
        Resources: rounded rectangles
        Edges:
            Resource -> Process: Allocation edge
            Process -> Resource: Request edge
        """
        deadlocked_set = set(deadlocked_pids or [])
        elements = []

        # Find cycles via Wait-For Graph to identify cycle participants
        proc_ids = [p['pid'] for p in processes]
        res_ids = [r['resource_id'] for r in resources]
        wfg = WaitForGraph(proc_ids, res_ids, allocation, request)
        wfg_analysis = wfg.get_analysis()
        cycle_nodes_proc = set(wfg_analysis['cycle_nodes'])

        # Process Nodes
        for p in processes:
            pid = p['pid']
            is_deadlocked = pid in deadlocked_set
            in_cycle = pid in cycle_nodes_proc
            elements.append({
                'data': {
                    'id': f"proc_{pid}",
                    'label': f"{p['name']} ({pid})",
                    'raw_id': pid,
                    'type': 'process',
                    'state': p.get('state', 'READY'),
                    'is_deadlocked': is_deadlocked,
                    'in_cycle': in_cycle
                }
            })

        # Resource Nodes
        for r in resources:
            rid = r['resource_id']
            elements.append({
                'data': {
                    'id': f"res_{rid}",
                    'label': f"{r['name']} ({rid})\nAvail: {r['available_instances']}/{r['total_instances']}",
                    'raw_id': rid,
                    'type': 'resource',
                    'total': r['total_instances'],
                    'available': r['available_instances']
                }
            })

        # Allocation Edges: Resource -> Process
        edge_id = 0
        for pid, res_dict in allocation.items():
            for rid, qty in res_dict.items():
                if qty > 0:
                    is_cycle_edge = (pid in cycle_nodes_proc)
                    elements.append({
                        'data': {
                            'id': f"alloc_{rid}_{pid}_{edge_id}",
                            'source': f"res_{rid}",
                            'target': f"proc_{pid}",
                            'label': f"Alloc: {qty}",
                            'quantity': qty,
                            'edge_type': 'allocation',
                            'in_cycle': is_cycle_edge
                        }
                    })
                    edge_id += 1

        # Request Edges: Process -> Resource
        for pid, res_dict in request.items():
            for rid, qty in res_dict.items():
                if qty > 0:
                    is_cycle_edge = (pid in cycle_nodes_proc)
                    elements.append({
                        'data': {
                            'id': f"req_{pid}_{rid}_{edge_id}",
                            'source': f"proc_{pid}",
                            'target': f"res_{rid}",
                            'label': f"Req: {qty}",
                            'quantity': qty,
                            'edge_type': 'request',
                            'in_cycle': is_cycle_edge
                        }
                    })
                    edge_id += 1

        return elements

    @staticmethod
    def build_wfg(
        processes: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        allocation: Dict[str, Dict[str, int]],
        request: Dict[str, Dict[str, int]],
        deadlocked_pids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Builds Cytoscape.js elements for the Wait-For Graph (WFG).
        """
        deadlocked_set = set(deadlocked_pids or [])
        proc_ids = [p['pid'] for p in processes]
        res_ids = [r['resource_id'] for r in resources]

        wfg = WaitForGraph(proc_ids, res_ids, allocation, request)
        analysis = wfg.get_analysis()

        cycle_nodes_set = set(analysis['cycle_nodes'])
        cycle_edges_set = {(e['from'], e['to']) for e in analysis['cycle_edges']}

        elements = []
        for p in processes:
            pid = p['pid']
            in_cycle = pid in cycle_nodes_set
            is_deadlocked = pid in deadlocked_set
            elements.append({
                'data': {
                    'id': f"wfg_{pid}",
                    'label': f"{p['name']} ({pid})",
                    'raw_id': pid,
                    'type': 'process',
                    'in_cycle': in_cycle,
                    'is_deadlocked': is_deadlocked
                }
            })

        for i, edge in enumerate(analysis['edges']):
            is_in_cycle = (edge['source'], edge['target']) in cycle_edges_set
            elements.append({
                'data': {
                    'id': f"wfg_edge_{i}",
                    'source': f"wfg_{edge['source']}",
                    'target': f"wfg_{edge['target']}",
                    'label': f"Waiting for {edge['resource']}",
                    'resource': edge['resource'],
                    'in_cycle': is_in_cycle
                }
            })

        return {
            'elements': elements,
            'cycles': analysis['cycles'],
            'has_cycles': analysis['has_cycles'],
            'explanation': analysis['explanation']
        }
