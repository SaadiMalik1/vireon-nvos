import os
import json
import pytest

@pytest.mark.skip(reason="Requires external literature dataset (not downloaded)")
def test_erp_p300():
    # ERP CORE P300 (Latency Target: 310ms)
    expected_latency = 310.0
    
    # In a real environment with the dataset downloaded:
    # from vireon_methods.native.erp import P300ERPMethod
    # from vireon_corpus.plugins.erp_core_plugin import ERPCOREPlugin
    # method = P300ERPMethod()
    # dataset = ERPCOREPlugin().load(subject_id="01", bids_root="...")
    # result = method.execute({"signal": dataset.data, "labels": dataset.labels})
    # actual_latency = extract_latency(result)
    # assert abs(actual_latency - expected_latency) < 10.0
    
    pass
    


if __name__ == "__main__":
    test_erp_p300()
