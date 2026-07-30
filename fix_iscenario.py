import os
filepath = 'vireon-core/tests/test_experiment_lifecycle.py'
with open(filepath, 'r') as f:
    content = f.read()
content = content.replace('IScenario', 'IExperimentDef') # Wait, IExperimentDef or IExperiment?
with open(filepath, 'w') as f:
    f.write(content)
