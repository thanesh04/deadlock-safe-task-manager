import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from config import TestingConfig
from database.database import db

def test_full_workflow():
    print("=" * 60)
    print("Executing End-to-End Operating Systems Simulation Workflow")
    print("=" * 60)

    app = create_app(TestingConfig)
    client = app.test_client()

    with app.app_context():
        # Step 1 & 2: Start application & Open dashboard
        dash_res = client.get('/')
        assert dash_res.status_code == 200
        print("[Step 1 & 2 PASSED] Application started & Dashboard rendered (200 OK)")

        # Step 3: Load Safe State scenario
        scen_res = client.post('/api/scenarios/load', json={'scenario_id': 'safe_state'})
        assert scen_res.status_code == 200 and scen_res.get_json()['success'] is True
        print("[Step 3 PASSED] Safe State scenario loaded")

        # Step 4: View matrices
        mat_res = client.get('/api/matrices')
        mat_data = mat_res.get_json()
        assert len(mat_data['processes']) == 5
        assert len(mat_data['resources']) == 3
        print(f"[Step 4 PASSED] Matrices extracted: 5 processes, 3 resources, Available: {mat_data['available']}")

        # Step 5 & 6: Run Safety Algorithm and verify safe sequence
        safe_res = client.post('/api/safety-check')
        safe_data = safe_res.get_json()
        assert safe_data['safe'] is True
        assert len(safe_data['safe_sequence']) == 5
        print(f"[Step 5 & 6 PASSED] Safety Algorithm computed SAFE state! Sequence: {' -> '.join(safe_data['safe_sequence'])}")

        # Step 7 & 8: Submit a valid resource request (P1 requests [1, 0, 2])
        req_res = client.post('/api/resource-request', json={
            'pid': 'P1',
            'request': {'R0': 1, 'R1': 0, 'R2': 2}
        })
        req_data = req_res.get_json()
        assert req_data['granted'] is True
        print(f"[Step 7 & 8 PASSED] Valid resource request for P1 GRANTED! Result: {req_data['reason']}")

        # Step 9, 10 & 11: Load Unsafe State scenario & verify UNSAFE
        scen_unsafe = client.post('/api/scenarios/load', json={'scenario_id': 'unsafe_state'})
        assert scen_unsafe.get_json()['success'] is True
        unsafe_check = client.post('/api/safety-check')
        unsafe_data = unsafe_check.get_json()
        assert unsafe_data['safe'] is False
        print(f"[Step 9, 10 & 11 PASSED] Unsafe scenario loaded. Verified UNSAFE state: {unsafe_data['summary']}")

        # Step 12, 13 & 14: Load Deadlock scenario & verify detection
        scen_deadlock = client.post('/api/scenarios/load', json={'scenario_id': 'two_process_deadlock'})
        assert scen_deadlock.get_json()['success'] is True
        det_res = client.post('/api/deadlock-detection')
        det_data = det_res.get_json()
        assert det_data['deadlock'] is True
        assert set(det_data['deadlocked_processes']) == {'P1', 'P2'}
        print(f"[Step 12, 13 & 14 PASSED] Deadlock scenario loaded. Deadlocked processes verified: {det_data['deadlocked_processes']}")

        # Step 15, 16 & 17: Open RAG and WFG and verify cycle visualization
        graph_res = client.get('/api/graphs')
        graph_data = graph_res.get_json()
        assert len(graph_data['rag_elements']) > 0
        assert len(graph_data['wfg_elements']) > 0
        assert graph_data['has_cycles'] is True
        print(f"[Step 15, 16 & 17 PASSED] Cytoscape RAG/WFG generated. Detected cycles: {graph_data['cycles']}")

        # Step 18 & 19: Perform recovery by terminating victim process P1
        rec_res = client.post('/api/recovery', json={
            'action_type': 'terminate',
            'params': {'pids': ['P1']}
        })
        rec_data = rec_res.get_json()
        assert rec_data['success'] is True
        assert rec_data['released']['R1'] == 1
        print(f"[Step 18 & 19 PASSED] Recovery executed. P1 terminated. Released resources: {rec_data['released']}")

        # Step 20 & 21: Re-run detection and verify deadlock resolution
        assert rec_data['deadlock_resolved'] is True
        post_det = client.post('/api/deadlock-detection').get_json()
        assert post_det['deadlock'] is False
        print(f"[Step 20 & 21 PASSED] Deadlock successfully RESOLVED! Re-run detection: DEADLOCK={post_det['deadlock']}")

        # Step 22 & 23: Reset scenario and verify original state restored
        reset_res = client.post('/api/simulation/reset')
        assert reset_res.status_code == 200
        post_reset_mat = client.get('/api/matrices').get_json()
        assert len(post_reset_mat['processes']) == 5
        print(f"[Step 22 & 23 PASSED] Simulation reset. Default safe state restored with 5 processes.")

    print("=" * 60)
    print("ALL 24 END-TO-END WORKFLOW VERIFICATION STEPS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_full_workflow()
