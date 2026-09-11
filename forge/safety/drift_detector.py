import numpy as np

class ConceptDriftDetector:
    """Calculates Population Stability Index (PSI) to detect adversarial baseline manipulation."""
    def __init__(self, psi_threshold=0.25):
        self.psi_threshold = psi_threshold

    def calculate_psi(self, baseline_distribution, current_distribution, num_buckets=10):
        baseline_pct, bins = np.histogram(baseline_distribution, bins=num_buckets, range=(0.0, 1.0))
        current_pct, _ = np.histogram(current_distribution, bins=bins)

        # Convert counts to proportions and apply epsilon smoothing
        eps = 1e-4
        b_prop = (baseline_pct / len(baseline_distribution)) + eps
        c_prop = (current_pct / len(current_distribution)) + eps

        psi_value = np.sum((c_prop - b_prop) * np.log(c_prop / b_prop))
        return float(psi_value)

    def is_drift_acceptable(self, baseline_data, current_data):
        psi = self.calculate_psi(baseline_data, current_data)
        print(f"[DriftDetector] Evaluated Telemetry PSI: {psi:.4f} (Threshold: {self.psi_threshold})")
        if psi > self.psi_threshold:
            print("[DriftDetector Warning] Significant statistical drift detected! Adversarial data poisoning possible.")
            return False
        return True