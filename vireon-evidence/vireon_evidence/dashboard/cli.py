from vireon_evidence.services.evidence_service import EvidenceService

class DashboardCLI:
    def __init__(self, service: EvidenceService):
        self.service = service
        
    def show_method(self, method_name: str):
        profile = self.service.get_method_profile(method_name)
        
        print(f"\n{method_name}")
        print("──────────────")
        print(f"Evidence: {profile['total_benchmarks']} Benchmarks\n")
        
        print("Datasets:")
        for ds in profile['datasets']:
            print(f"✓ {ds}")
            
        print("\nMetrics:")
        for k, v in profile['metrics'].items():
            print(f"- {k}: {v}")
            
        print(f"\nCurrent SRL: {profile['current_srl']}")
        print(f"\nFailure Cases: {', '.join(profile['failure_cases'])}")
        print(f"Publications: {', '.join(profile['publications'])}\n")
