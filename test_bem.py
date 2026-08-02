import numpy as np
from vireon_models.source_space import BEMModel

print("Creating BEMModel...")
model = BEMModel(bem_file_path="")
try:
    print("Computing leadfield...")
    lf = model.compute_leadfield(np.zeros((1,3)), np.zeros((1,3)))
    print("Success, shape:", lf.shape)
except Exception as e:
    print("Error:", e)
