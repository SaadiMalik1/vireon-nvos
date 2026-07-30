import os
import glob
from typing import List, Dict, Any
from vireon_core.contracts import IExperimentDef
from vireon_lab.experiments.schema import load_experiment_from_yaml

class ExperimentRegistry:
    """
    Registry for discovering and loading available experiments from disk.
    """
    def __init__(self, experiments_dir: str):
        self.experiments_dir = experiments_dir
        
    def get_experiment(self, name: str) -> IExperimentDef:
        path = os.path.join(self.experiments_dir, f"{name}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Experiment {name} not found at {path}")
        return load_experiment_from_yaml(path)

    def list_experiments(self) -> List[str]:
        files = glob.glob(os.path.join(self.experiments_dir, "*.yaml"))
        return [os.path.basename(f).replace(".yaml", "") for f in files]


class CampaignRegistry:
    """
    Registry for defining test campaigns composed of multiple experiments.
    """
    def __init__(self, experiment_registry: ExperimentRegistry):
        self.experiment_registry = experiment_registry
        
        # In a real system, campaigns would also be loaded from disk or a database.
        # For this implementation, we define them here.
        self.campaigns = {
            "all": self.experiment_registry.list_experiments(),
            "campaign_2": ["decoder_robustness"],
            "campaign_3": ["cybersecurity"]
        }
        
    def get_campaign_experiments(self, campaign_name: str) -> List[IExperimentDef]:
        if campaign_name not in self.campaigns:
            # Maybe the campaign_name is actually a single experiment name
            if campaign_name in self.experiment_registry.list_experiments():
                return [self.experiment_registry.get_experiment(campaign_name)]
            raise ValueError(f"Campaign or experiment '{campaign_name}' not found.")
            
        experiment_names = self.campaigns[campaign_name]
        return [self.experiment_registry.get_experiment(name) for name in experiment_names]
