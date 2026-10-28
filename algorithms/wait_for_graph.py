"""
Wait-For Graph (WFG) Construction and Cycle Detection.
In a Wait-For Graph, nodes represent processes. A directed edge P_i -> P_j
indicates that process P_i is waiting for a resource currently allocated to P_j.
A cycle in the Wait-For Graph indicates a circular wait condition.
"""
from typing import Dict, List, Set, Tuple, Any

class WaitForGraph:
    def __init__(
        self,
        processes: List[str],
        resources: List[str],
        allocation: Dict[str, Dict[str, int]],
        request: Dict[str, Dict[str, int]]
    ):
        self.processes = list(processes)
        self.resources = list(resources)
        self.allocation = allocation
        self.request = request
        self.adj_list: Dict[str, Set[str]] = {p: set() for p in self.processes}
        self.edge_details: List[Dict[str, Any]] = []
        self._build_graph()

    def _build_graph(self):
        """
        Constructs the wait-for edges:
        If P_i requests resource R_k (> 0) and P_j holds R_k (> 0),
        add directed edge P_i -> P_j.
        """
        for pi in self.processes:
            for r in self.resources:
                req_val = self.request.get(pi, {}).get(r, 0)
                if req_val > 0:
                    for pj in self.processes:
                        if pi == pj:
                            continue
                        alloc_val = self.allocation.get(pj, {}).get(r, 0)
                        if alloc_val > 0:
                            if pj not in self.adj_list[pi]:
                                self.adj_list[pi].add(pj)
                                self.edge_details.append({
                                    'from': pi,
                                    'to': pj,
                                    'resource': r,
                                    'requested': req_val,
                                    'held': alloc_val
                                })

    def find_cycles(self) -> List[List[str]]:
        """
        Detects all simple cycles in the directed graph using depth-first search.
        Returns a list of cycle paths, e.g. [['P1', 'P2', 'P1']].
        """
        cycles: List[List[str]] = []
        visited_nodes: Set[str] = set()

        def dfs(curr: str, path: List[str], path_set: Set[str]):
            for neighbor in self.adj_list.get(curr, set()):
                if neighbor in path_set:
                    # Found cycle: extract from first occurrence
                    cycle_start_idx = path.index(neighbor)
                    cycle = path[cycle_start_idx:] + [neighbor]
                    # Canonicalize cycle (rotate so smallest node is first) to eliminate duplicates
                    canonical = self._canonicalize_cycle(cycle)
                    if canonical not in cycles:
                        cycles.append(canonical)
                elif neighbor not in path:
                    path.append(neighbor)
                    path_set.add(neighbor)
                    dfs(neighbor, path, path_set)
                    path.pop()
                    path_set.remove(neighbor)

        for p in self.processes:
            dfs(p, [p], {p})

        return cycles

    def _canonicalize_cycle(self, cycle: List[str]) -> List[str]:
        """Rotates a cycle so the lexicographically smallest element is first."""
        base = cycle[:-1]
        min_idx = base.index(min(base))
        rotated = base[min_idx:] + base[:min_idx]
        return rotated + [rotated[0]]

    def get_analysis(self) -> Dict[str, Any]:
        """
        Analyzes the Wait-For Graph and returns structure and detected cycles.
        """
        cycles = self.find_cycles()
        has_deadlock = len(cycles) > 0

        # Collect cycle nodes and edges for visual highlighting
        cycle_nodes: Set[str] = set()
        cycle_edges: Set[Tuple[str, str]] = set()

        for c in cycles:
            for i in range(len(c) - 1):
                cycle_nodes.add(c[i])
                cycle_edges.add((c[i], c[i + 1]))

        formatted_edges = []
        for e in self.edge_details:
            is_in_cycle = (e['from'], e['to']) in cycle_edges
            formatted_edges.append({
                'source': e['from'],
                'target': e['to'],
                'resource': e['resource'],
                'requested': e['requested'],
                'held': e['held'],
                'in_cycle': is_in_cycle
            })

        return {
            'nodes': self.processes,
            'edges': formatted_edges,
            'cycles': cycles,
            'has_cycles': has_deadlock,
            'cycle_nodes': list(cycle_nodes),
            'cycle_edges': [{'from': u, 'to': v} for u, v in cycle_edges],
            'explanation': (
                f"Deadlock detected in Wait-For Graph! Found {len(cycles)} cycle(s): "
                + ", ".join([" -> ".join(c) for c in cycles])
                if has_deadlock else "No cycles detected in Wait-For Graph."
            )
        }
