## NP-KG Evaluation (case studies green tea and kratom)

NP-KG has been evaluated with case studies of pharmacokinetic green tea- and kratom-drug interactions involving enzymes and transporters. This folder contains the Jupyter notebooks used for the evaluation strategies described below.

### I. Knowledge Recapturing

1. Direct Edges
_[KG-mechanistic-knowledge-recapture.ipynb](https://github.com/sanyabt/np-kg/blob/main/evaluation-notebooks/KG-mechanistic-knowledge-recapture.ipynb)_ finds direct edges between natural product nodes (natural products and their constituents) and interacting enzymes and transporters (if any).

2. Shortest Path Searches
_[KG-mechanistic-knowledge-shortest-paths.ipynb](https://github.com/sanyabt/np-kg/blob/main/evaluation-notebooks/KG-mechanistic-knowledge-shortest-paths.ipynb)_ finds the shortest paths between the natural product and interacting enzymes and transporters, if there are no direct edges between them.

### II. Meta-path Discovery
_[KG-metapath-discovery.ipynb](https://github.com/sanyabt/np-kg/blob/main/evaluation-notebooks/KG-metapath-discovery.ipynb)_ applies direct edge and meta-path searches to find mechanistic pathways between natural product nodes and drugs, with interacting enzymes or transporters. Meta-path searches are applied for the following natural product-drug pairs:

* Green tea - raloxifene
* Green tea - nadolol
* Kratom - midazolam
* Kratom - quetiapene
* Kratom - venlafaxine

#### Ground Truth
All searches above are evaluated based on the ground truth data from the [NaPDI Center database](https://repo.napdi.org/).