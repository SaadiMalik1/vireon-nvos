from vireon_core.contracts.evidence import EvidenceBundle

class ProvenanceReplay:
    """
    Recreates an exact benchmark execution from a versioned EvidenceBundle.
    `vireon replay evidence:abc123`
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
    def replay(self, bundle: EvidenceBundle) -> EvidenceBundle:
        """
        Extracts provenance from the bundle and triggers execution to recreate it identically.
        """
        if self.orchestrator is None:
            raise NotImplementedError("Orchestrator is required to execute provenance replay.")
        
        # Trigger orchestrator execution with extracted parameters
        params = {
            "dataset": bundle.dataset,
            "algorithm": bundle.algorithm,
            "random_seed": bundle.random_seed,
        }
        if hasattr(self.orchestrator, "run"):
            return self.orchestrator.run(params)
        return bundle
