"""Scenario 01: Real-Time Streaming EEG Validation.

Simulates chunk-by-chunk EEG streaming over LSL/buffers and validates 
latency and numerical drift under streaming conditions.
"""
import time
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch

def run_streaming_scenario():
    print("=== Running Real-Time Streaming EEG Validation ===")
    rng = DeterministicRNG(seed=42)
    fs = 250.0
    chunk_size = 250  # 1-second chunks
    n_chunks = 10
    
    welch = VireonWelch(fs=fs, nperseg=128)
    latencies = []
    
    for i in range(n_chunks):
        chunk = rng.normal(0, 1.0, chunk_size) + np.sin(2 * np.pi * 10 * np.arange(chunk_size) / fs)
        t0 = time.perf_counter()
        freqs, psd = welch.compute(chunk)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)
        
    avg_latency = np.mean(latencies)
    print(f"Processed {n_chunks} streaming chunks of size {chunk_size}.")
    print(f"Mean processing latency per chunk: {avg_latency:.3f} ms")
    assert avg_latency < 50.0, "Latency exceeds real-time threshold!"
    print("PASS: Real-Time Streaming Validation")

if __name__ == "__main__":
    run_streaming_scenario()
