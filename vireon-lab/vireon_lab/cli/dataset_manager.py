import os
import sys

# In a real dynamic system, these would be discovered via entry_points
from vireon_corpus.plugins.eegbci_plugin import EEGBCIPlugin
from vireon_corpus.plugins.sleep_edf_plugin import SleepEDFPlugin
from vireon_corpus.plugins.erp_core_plugin import ERPCOREPlugin

PLUGINS = {
    "eegbci": EEGBCIPlugin,
    "sleep-edf": SleepEDFPlugin,
    "erp-core": ERPCOREPlugin,
}

def get_available_datasets():
    return list(PLUGINS.keys())

def fetch_dataset(name: str, base_dir: str):
    if name not in PLUGINS:
        print(f"Unknown dataset: {name}. Available: {get_available_datasets()}")
        sys.exit(1)
        
    plugin = PLUGINS[name]()
    
    # Define paths
    corpus_dir = os.path.join(base_dir, "vireon-corpus")
    cache_dir = os.path.join(corpus_dir, "cache", name)
    bids_dir = os.path.join(corpus_dir, "datasets", "bids")
    manifest_dir = os.path.join(corpus_dir, "manifests")
    
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(bids_dir, exist_ok=True)
    os.makedirs(manifest_dir, exist_ok=True)
    
    print(f"[{name}] Starting fetch protocol via {plugin.plugin_id} (SRL: {plugin.srl.name})")
    
    # 1. Download
    print(f"[{name}] Downloading to local cache...")
    plugin.download(cache_dir)
    
    # 2. Verify Checksum & License
    print(f"[{name}] Verifying checksums...")
    if not plugin.verify_checksum(cache_dir):
        print(f"[{name}] ERROR: Checksum mismatch. Aborting.")
        sys.exit(1)
        
    print(f"[{name}] Verifying license compliance...")
    plugin.verify_license()
    
    # 3. Convert to BIDS
    print(f"[{name}] Converting to canonical BIDS structure...")
    plugin.convert_to_bids(cache_dir, bids_dir)
    
    # 4. Generate metadata & manifests
    print(f"[{name}] Generating checksum hashes and manifests...")
    bids_root = os.path.join(bids_dir, name)
    plugin.generate_metadata(bids_root)
    plugin.generate_hash(bids_root)
    plugin.create_manifest(os.path.join(manifest_dir, f"{name}_manifest.json"))
    
    print(f"[{name}] Fetch complete. Dataset integrated into VIREON corpus.")
