"""
Simulator: Central coordinator between database models, OS algorithms, and API/UI.
Provides unified methods to extract matrices, evaluate safety, handle requests,
detect deadlocks, and perform recovery.
"""
from typing import Dict, List, Tuple, Any, Optional
from database.database import db
from database.models import Process, Resource, Allocation, MaximumNeed, ResourceRequest, EventLog, ProcessState
from algorithms.bankers import BankersAlgorithm
from algorithms.safety import SafetyAlgorithm
from algorithms.resource_request import ResourceRequestAlgorithm
from algorithms.deadlock_detection import DeadlockDetectionAlgorithm
from algorithms.recovery import DeadlockRecovery
from algorithms.wait_for_graph import WaitForGraph
from algorithms.graph_builder import GraphBuilder

class Simulator:
    @staticmethod
    def get_system_matrices() -> Dict[str, Any]:
        """
        Extracts Available vector, Allocation matrix, Maximum matrix,
        Need matrix, and active Request vector.
        """
        processes = Process.query.filter(Process.state != ProcessState.TERMINATED).order_by(Process.pid).all()
        resources = Resource.query.order_by(Resource.resource_id).all()

        pids = [p.pid for p in processes]
        rids = [r.resource_id for r in resources]

        available = {r.resource_id: r.available_instances for r in resources}
        total = {r.resource_id: r.total_instances for r in resources}

        allocation: Dict[str, Dict[str, int]] = {p: {r: 0 for r in rids} for p in pids}
        maximum: Dict[str, Dict[str, int]] = {p: {r: 0 for r in rids} for p in pids}
        need: Dict[str, Dict[str, int]] = {p: {r: 0 for r in rids} for p in pids}
        request: Dict[str, Dict[str, int]] = {p: {r: 0 for r in rids} for p in pids}

        for p in processes:
            for a in p.allocations:
                if a.resource and a.resource.resource_id in rids:
                    allocation[p.pid][a.resource.resource_id] = a.allocated
            for m in p.maximums:
                if m.resource and m.resource.resource_id in rids:
                    maximum[p.pid][m.resource.resource_id] = m.maximum
            for r in rids:
                need[p.pid][r] = max(0, maximum[p.pid][r] - allocation[p.pid][r])

            # Pending requests
            pending_req = next((req for req in p.requests if req.status == 'PENDING'), None)
            if pending_req and isinstance(pending_req.request_data, dict):
                for r in rids:
                    request[p.pid][r] = int(pending_req.request_data.get(r, 0))

        return {
            'processes': pids,
            'resources': rids,
            'available': available,
            'total': total,
            'allocation': allocation,
            'maximum': maximum,
            'need': need,
            'request': request
        }

    @staticmethod
    def check_safety() -> Dict[str, Any]:
        """Runs the Safety Algorithm on current system state."""
        state = Simulator.get_system_matrices()
        bankers = BankersAlgorithm(
            processes=state['processes'],
            resources=state['resources'],
            available=state['available'],
            allocation=state['allocation'],
            maximum=state['maximum']
        )
        result = bankers.is_safe()
        result['matrices'] = state

        # Log check
        log = EventLog(
            event_type="SAFETY_CHECK",
            description=f"Executed Safety Algorithm: {'SAFE' if result.get('safe') else 'UNSAFE'}. Sequence: {' -> '.join(result.get('safe_sequence', [])) if result.get('safe') else 'None'}."
        )
        db.session.add(log)
        db.session.commit()
        return result

    @staticmethod
    def process_resource_request(pid: str, request_vector: Dict[str, int]) -> Dict[str, Any]:
        """
        Executes Banker's Resource-Request Algorithm.
        If safe: commits allocation and updates available resources.
        If unsafe: rejects and records reason.
        """
        process = Process.query.filter_by(pid=pid.upper()).first()
        if not process:
            return {'success': False, 'message': f"Process '{pid}' not found."}

        state = Simulator.get_system_matrices()
        req_algo = ResourceRequestAlgorithm(
            processes=state['processes'],
            resources=state['resources'],
            available=state['available'],
            allocation=state['allocation'],
            maximum=state['maximum'],
            need=state['need']
        )

        eval_result = req_algo.evaluate_request(pid=process.pid, request=request_vector)

        # Record in ResourceRequest model
        req_record = ResourceRequest(
            process_id=process.id,
            request_data=request_vector,
            status='GRANTED' if eval_result['granted'] else 'DENIED',
            reason=eval_result['reason']
        )
        db.session.add(req_record)

        if eval_result['granted']:
            # Commit changes to database
            res_map = {r.resource_id: r for r in Resource.query.all()}
            for a in process.allocations:
                rid = a.resource.resource_id
                qty = int(request_vector.get(rid, 0))
                if qty > 0:
                    a.allocated += qty
                    res_map[rid].available_instances -= qty

            if process.state in [ProcessState.READY, ProcessState.WAITING]:
                process.state = ProcessState.RUNNING

            log_desc = f"Granted request for {process.pid}: {request_vector}. Safe sequence: {' -> '.join(eval_result.get('safety_analysis', {}).get('safe_sequence', []))}."
            event_type = "REQUEST_GRANTED"
        else:
            if eval_result.get('step_failed') == 2:
                # Insufficient availability -> process enters waiting
                process.state = ProcessState.WAITING
            log_desc = f"Denied request for {process.pid}: {request_vector}. Reason: {eval_result['reason']}"
            event_type = "REQUEST_DENIED"

        db.session.add(EventLog(event_type=event_type, description=log_desc))
        db.session.commit()

        eval_result['success'] = True
        return eval_result

    @staticmethod
    def detect_deadlock() -> Dict[str, Any]:
        """Runs the Deadlock Detection Algorithm and updates process states."""
        state = Simulator.get_system_matrices()
        detector = DeadlockDetectionAlgorithm(
            processes=state['processes'],
            resources=state['resources'],
            available=state['available'],
            allocation=state['allocation'],
            request=state['request']
        )
        result = detector.run()
        result['matrices'] = state

        # Update process states in database based on deadlock detection
        deadlocked_set = set(result['deadlocked_processes'])
        processes = Process.query.filter(Process.state != ProcessState.TERMINATED).all()
        for p in processes:
            if p.pid in deadlocked_set:
                p.state = ProcessState.DEADLOCKED
            elif p.state == ProcessState.DEADLOCKED:
                p.state = ProcessState.READY

        log = EventLog(
            event_type="DEADLOCK_DETECTION",
            description=f"Deadlock Detection executed: {'DEADLOCK DETECTED' if result['deadlock'] else 'NO DEADLOCK'}. Deadlocked: {', '.join(result['deadlocked_processes']) if result['deadlock'] else 'None'}."
        )
        db.session.add(log)
        db.session.commit()
        return result

    @staticmethod
    def recover_deadlock(action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes deadlock recovery:
        action_type: 'terminate' or 'preempt'
        """
        state = Simulator.get_system_matrices()
        recovery = DeadlockRecovery(
            processes=state['processes'],
            resources=state['resources'],
            available=state['available'],
            allocation=state['allocation'],
            request=state['request']
        )

        if action_type == 'terminate':
            pids = params.get('pids', [])
            if isinstance(pids, str):
                pids = [pids]

            # Execute actual database termination
            total_released = {}
            for pid in pids:
                p = Process.query.filter_by(pid=pid).first()
                if p:
                    for a in p.allocations:
                        qty = a.allocated
                        if qty > 0 and a.resource:
                            a.resource.available_instances += qty
                            total_released[a.resource.resource_id] = total_released.get(a.resource.resource_id, 0) + qty
                            a.allocated = 0
                    p.state = ProcessState.TERMINATED
                    # Cancel requests
                    for req in p.requests:
                        if req.status == 'PENDING':
                            req.status = 'CANCELLED'

            db.session.commit()

            # Now run detection on updated state
            post_state = Simulator.get_system_matrices()
            detector = DeadlockDetectionAlgorithm(
                processes=post_state['processes'],
                resources=post_state['resources'],
                available=post_state['available'],
                allocation=post_state['allocation'],
                request=post_state['request']
            )
            detection_res = detector.run()

            # Update states of remaining processes
            rem_deadlocked = set(detection_res['deadlocked_processes'])
            for p in Process.query.filter(Process.state != ProcessState.TERMINATED).all():
                if p.pid in rem_deadlocked:
                    p.state = ProcessState.DEADLOCKED
                elif p.state == ProcessState.DEADLOCKED:
                    p.state = ProcessState.READY

            log = EventLog(
                event_type="DEADLOCK_RECOVERY",
                description=f"Terminated processes {', '.join(pids)}. Released {total_released}. Deadlock resolved: {not detection_res['deadlock']}."
            )
            db.session.add(log)
            db.session.commit()

            return {
                'success': True,
                'action': 'TERMINATE',
                'terminated': pids,
                'released': total_released,
                'deadlock_resolved': not detection_res['deadlock'],
                'remaining_deadlocked': detection_res['deadlocked_processes'],
                'detection': detection_res
            }

        elif action_type == 'preempt':
            # Educational simulation
            victim = params.get('victim_pid')
            target = params.get('target_pid')
            resource = params.get('resource_id')
            qty = int(params.get('quantity', 1))

            sim_res = recovery.simulate_preemption(
                victim_pid=victim,
                target_pid=target,
                resource_id=resource,
                quantity=qty
            )
            db.session.add(EventLog(
                event_type="RECOVERY_SIMULATION",
                description=sim_res.get('message', 'Preemption simulation executed.')
            ))
            db.session.commit()
            return sim_res

        return {'success': False, 'message': f"Unknown recovery action: {action_type}"}

    @staticmethod
    def get_graphs_data() -> Dict[str, Any]:
        """Provides Cytoscape-formatted data for RAG, WFG, and cycles."""
        processes = [p.to_dict() for p in Process.query.filter(Process.state != ProcessState.TERMINATED).all()]
        resources = [r.to_dict() for r in Resource.query.all()]
        matrices = Simulator.get_system_matrices()

        # Run deadlock detection to identify deadlocked nodes
        detector = DeadlockDetectionAlgorithm(
            processes=matrices['processes'],
            resources=matrices['resources'],
            available=matrices['available'],
            allocation=matrices['allocation'],
            request=matrices['request']
        )
        det_result = detector.run()
        deadlocked_pids = det_result['deadlocked_processes']

        rag_elements = GraphBuilder.build_rag(
            processes=processes,
            resources=resources,
            allocation=matrices['allocation'],
            request=matrices['request'],
            deadlocked_pids=deadlocked_pids
        )

        wfg_data = GraphBuilder.build_wfg(
            processes=processes,
            resources=resources,
            allocation=matrices['allocation'],
            request=matrices['request'],
            deadlocked_pids=deadlocked_pids
        )

        return {
            'rag_elements': rag_elements,
            'wfg_elements': wfg_data['elements'],
            'cycles': wfg_data['cycles'],
            'has_cycles': wfg_data['has_cycles'],
            'explanation': wfg_data['explanation'],
            'deadlocked_processes': deadlocked_pids
        }

    @staticmethod
    def clear_all_data():
        """Clears all processes, resources, allocations, requests, and logs."""
        Allocation.query.delete()
        MaximumNeed.query.delete()
        ResourceRequest.query.delete()
        Process.query.delete()
        Resource.query.delete()
        EventLog.query.delete()
        db.session.commit()
