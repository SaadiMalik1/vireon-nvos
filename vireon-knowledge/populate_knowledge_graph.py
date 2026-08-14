import json
import os

def populate():
    print("=== VIREON Knowledge Graph Synthesis ===")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ontologies_dir = os.path.join(base_dir, "vireon_knowledge")
    
    graph = {
        "nodes": [],
        "edges": []
    }
    
    # Load methods
    methods_file = os.path.join(ontologies_dir, "methodologies", "methods.jsonld")
    if os.path.exists(methods_file):
        with open(methods_file, "r") as f:
            data = json.load(f)
            for m_key, m_val in data.get("methods", {}).items():
                node_id = m_val.get("@id")
                graph["nodes"].append({
                    "id": node_id,
                    "type": "Method",
                    "description": m_val.get("name", "")
                })
                # Edges for assumptions
                for assumption_id in m_val.get("assumptions", []):
                    graph["edges"].append({
                        "source": node_id,
                        "target": assumption_id,
                        "relationship": "REQUIRES"
                    })
                    
    # Load assumptions
    assumptions_file = os.path.join(ontologies_dir, "assumptions", "assumptions.jsonld")
    if os.path.exists(assumptions_file):
        with open(assumptions_file, "r") as f:
            data = json.load(f)
            for a_key, a_val in data.get("assumptions", {}).items():
                graph["nodes"].append({
                    "id": a_val.get("@id"),
                    "type": "Assumption",
                    "description": a_val.get("description", "")
                })
                
    # Load methodology
    methodology_file = os.path.join(ontologies_dir, "ontologies", "methodology.jsonld")
    if os.path.exists(methodology_file):
        with open(methodology_file, "r") as f:
            data = json.load(f)
            if "methods" in data:
                for m_key, m_val in data["methods"].items():
                    node_id = m_val.get("@id")
                    graph["nodes"].append({
                        "id": node_id,
                        "type": "Method",
                        "description": m_val.get("name", "")
                    })
                    for assumption_id in m_val.get("assumptions", []):
                        graph["edges"].append({
                            "source": node_id,
                            "target": assumption_id,
                            "relationship": "REQUIRES"
                        })
            if "assumptions" in data:
                for a_key, a_val in data["assumptions"].items():
                    graph["nodes"].append({
                        "id": a_val.get("@id"),
                        "type": "Assumption",
                        "description": a_val.get("description", "")
                    })
                
    # We could load rules, ontologies, etc. but let's stick to the main structure for now.
    
    print(f"Added {len(graph['nodes'])} formal ontology nodes.")
    print(f"Added {len(graph['edges'])} explicit relationships.")
    
    with open(os.path.join(base_dir, "knowledge_snapshot.json"), "w") as f:
        json.dump(graph, f, indent=4)
        
if __name__ == "__main__":
    populate()
