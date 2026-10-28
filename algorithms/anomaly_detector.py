"""
Process Behavior Anomaly & Starvation Detector.
Analyzes process resource demands, waiting patterns, greed indices, and starvation risks.
"""
from typing import Dict, List, Any

class ProcessAnomalyDetector:
    """
    Evaluates processes for:
    1. Greed Index (High claim relative to total system capacity)
    2. Starvation Risk (Consecutively denied safety requests)
    3. Resource Hoarding (Holding resources while idle/blocked)
    4. Deadlock Contention Risk (Holding resources that high-priority tasks need)
    """

    @staticmethod
    def calculate_greed_index(max_claim: Dict[str, int], total_resources: Dict[str, int]) -> float:
        """
        Calculates the ratio of a process's maximum resource demand to the total system capacity.
        Returns a percentage 0.0 - 100.0%.
        """
        total_capacity_units = sum(total_resources.values())
        if total_capacity_units == 0:
            return 0.0
        
        claim_units = sum(max_claim.get(r, 0) for r in total_resources)
        ratio = (claim_units / total_capacity_units) * 100.0
        return round(min(100.0, max(0.0, ratio)), 1)

    @staticmethod
    def evaluate_process(
        pid: str,
        state: str,
        burst_progress: float,
        held_resources: Dict[str, int],
        pending_request: Dict[str, int],
        max_claim: Dict[str, int],
        total_resources: Dict[str, int],
        starvation_ticks: int,
        aging_threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Generates an anomaly report for a single process.
        """
        greed = ProcessAnomalyDetector.calculate_greed_index(max_claim, total_resources)
        is_hoarding = sum(held_resources.values()) > 0 and state in ["SAFETY_WAIT", "WAITING"]
        is_starving = starvation_ticks >= aging_threshold

        anomalies = []
        severity = "NORMAL"
        risk_score = 0  # 0 to 100

        # Greed check
        if greed >= 65.0:
            anomalies.append(f"High Resource Greed ({greed}% of system capacity)")
            risk_score += 35
        elif greed >= 40.0:
            risk_score += 15

        # Starvation check
        if is_starving:
            anomalies.append(f"Starvation Risk: Blocked for {starvation_ticks} consecutive cycles")
            risk_score += min(50, starvation_ticks * 12)
            severity = "HIGH" if starvation_ticks >= aging_threshold * 2 else "WARNING"
        elif starvation_ticks > 0:
            risk_score += starvation_ticks * 5

        # Hoarding check
        if is_hoarding:
            held_count = sum(held_resources.values())
            anomalies.append(f"Resource Hoarder: Holding {held_count} units while blocked/waiting")
            risk_score += 25
            if severity == "NORMAL":
                severity = "WARNING"

        risk_score = min(100, risk_score)

        if risk_score >= 70:
            severity = "CRITICAL"
        elif risk_score >= 40:
            severity = "WARNING"

        return {
            "pid": pid,
            "greed_index": greed,
            "starvation_ticks": starvation_ticks,
            "is_hoarding": is_hoarding,
            "is_starving": is_starving,
            "risk_score": risk_score,
            "severity": severity,
            "anomalies": anomalies,
            "description": "; ".join(anomalies) if anomalies else "Normal behavior"
        }
