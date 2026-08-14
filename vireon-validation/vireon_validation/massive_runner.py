import sys
from vireon_validation.benchmarks.orchestrator import MassiveCampaignOrchestrator
from vireon_validation.benchmarks.meta_analysis import MetaAnalysisEngine, PublicationExporter

def main():
    with open(sys.argv[1], 'r') as f:
        yaml_content = f.read()
        
    orchestrator = MassiveCampaignOrchestrator.from_yaml(yaml_content)
    results = orchestrator.execute()
    
    print("=== MASSIVE CAMPAIGN EXECUTION ===")
    print(f"Total Factorial Runs Executed: {results['total_factorial_runs']}")
    print(f"Operational Envelopes Generated: {results['operational_envelopes_generated']}")
    print(f"Failures Logged to FailureAtlas: {results['failures_logged']}")
    
    # Meta Analysis
    engine = MetaAnalysisEngine([results])
    stats = engine.compute_statistics()
    
    print("\n=== META-ANALYSIS RESULTS ===")
    print(f"Global Mean Performance: {stats['global_mean_performance']}")
    print(f"Confidence Interval: {stats['confidence_interval']}")
    print(f"Heterogeneity (I2): {stats['heterogeneity_i2']}%")
    print("\nOperational Envelope Bound:")
    print(stats['operational_envelope'])
    
    # Exporter
    print("")
    exporter = PublicationExporter(stats)
    exporter.export("./publications")

if __name__ == "__main__":
    main()
