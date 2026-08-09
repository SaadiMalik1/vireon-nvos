import os
import json
import time

def test_interoperability():
    results = {}
    
    # Tier 1: MNE
    try:
        import mne
    except ImportError:
        print("MNE is required for Interoperability testing.")
        return

    # Create dummy raw object
    info = mne.create_info(ch_names=['O1', 'O2'], sfreq=250.0, ch_types=['eeg', 'eeg'])
    from vireon_core.runtime.rng import DeterministicRNG
    rng = DeterministicRNG(seed=42)
    
    # 1. Create a dummy MNE raw object
    data = rng.normal(0.0, 1.0, (2, 2500))
    raw = mne.io.RawArray(data, info)
    
    # 1. EDF Export/Import
    try:
        import pyedflib
        import mne.export
        edf_path = os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results/test.edf")
        os.makedirs(os.path.dirname(edf_path), exist_ok=True)
        mne.export.export_raw(edf_path, raw, fmt='edf', overwrite=True)
        raw_edf = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        
        # Verify metadata
        sfreq_match = raw.info['sfreq'] == raw_edf.info['sfreq']
        ch_match = raw.ch_names == raw_edf.ch_names
        
        results["EDF_Roundtrip"] = {
            "status": "PASS" if sfreq_match and ch_match else "FAIL",
            "reason": "Metadata preserved" if sfreq_match and ch_match else "Metadata lost"
        }
    except ImportError:
        results["EDF_Roundtrip"] = {"status": "SKIPPED", "reason": "Missing dependency: pyedflib or mne.export"}

    # 2. BIDS Export
    try:
        import mne_bids
        from mne_bids import BIDSPath, write_raw_bids
        bids_root = os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results/bids")
        bids_path = BIDSPath(subject='01', task='test', root=bids_root)
        write_raw_bids(raw, bids_path, overwrite=True, allow_preload=True, format='EDF', verbose=False)
        
        results["BIDS_Export"] = {"status": "PASS", "reason": "BIDS structure generated"}
    except ImportError:
        results["BIDS_Export"] = {"status": "SKIPPED", "reason": "Missing dependency: mne-bids"}

    # 3. LSL Stream Roundtrip
    try:
        from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
        import threading
        
        # Setup Outlet
        lsl_info = StreamInfo('VIREON_Test', 'EEG', 2, 250, 'float32', 'myuid34234')
        outlet = StreamOutlet(lsl_info)
        
        # Setup Inlet in thread
        received_samples = []
        def receive_lsl():
            streams = resolve_stream('type', 'EEG')
            inlet = StreamInlet(streams[0])
            for _ in range(10):
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample:
                    received_samples.append(sample)
                    
        t = threading.Thread(target=receive_lsl)
        t.start()
        
        # Push data
        for i in range(10):
            outlet.push_sample([1.0, 2.0])
            time.sleep(0.004) # 250Hz
            
        t.join(timeout=2.0)
        
        if len(received_samples) > 0 and received_samples[0] == [1.0, 2.0]:
            results["LSL_Roundtrip"] = {"status": "PASS", "reason": "LSL streaming succeeded"}
        else:
            results["LSL_Roundtrip"] = {"status": "FAIL", "reason": "LSL samples not received"}
            
    except ImportError:
        results["LSL_Roundtrip"] = {"status": "SKIPPED", "reason": "Missing dependency: pylsl"}

    metrics_path = os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results/interoperability_metrics.json")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=4)
        
    for k, v in results.items():
        print(f"[{v['status']}] {k}: {v['reason']}")

if __name__ == "__main__":
    test_interoperability()
