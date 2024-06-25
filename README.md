[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12536780.svg)](https://doi.org/10.5281/zenodo.12536780)

# NP-KG

**Knowledge Graph Framework to Generate Hypotheses for Natural Product-Drug Interactions**

NP-KG is a graph framework that creates a biomedical knowledge graph (KG) to identify and generate mechanistic hypotheses for pharmacokinetic natural product-drug interactions (NPDIs). NP-KG uses the [PheKnowLator ecosystem](https://github.com/callahantiff/PheKnowLator) to create an ontology-grounded KG. It then uses two relation extraction systems to extract triples from full texts of natural product-related scientific literature to create a literature-based graph, and integrates the nodes and edges in the ontology-grounded KG. 

## NP-KG Builds

**NP-KG:** Merged PheKnowLator KG and literature-based graph with 30 natural products.

**Ontology-grounded KG:** PheKnowLator KG with a few [additional data sources](https://github.com/sanyabt/np-kg/wiki/v3.0.0#data-sources).

**Literature-based Graph:** Literature-based graph constructed from scientific literature with relation extraction systems (SemRep and INDRA/REACH) and closure operations.

## How to Download and Use

### Setup environment

1. Clone the repository or download all files.
2. Install all required packages. Requires Python>=3.6.

```
python -m pip install -r requirements.txt
```

### If you want to use the pre-built KGs

1. [Download the knowledge graph and node labels files from Zenodo](https://doi.org/10.5281/zenodo.12536780) and add to local folder - resources/knowledge_graphs. NP-KG is available as TSV file with triples and NetworkX multidigraph (gpickle files).

* **Merged KG:** includes merged PheKnowLator KG and literature-based graph. Download this file if you do not know which KG to use.
	* Filename: _NP-KG_v3.0.0.tsv_
	* Filename: _NP-KG_v3.0.0.gpickle_
* **PheKnowLator KG:** includes full instance-based build of the PheKnowLator KG. See [PheKnowLator](https://github.com/callahantiff/PheKnowLator) for more details.
	* Filename: _PheKnowLator_v3.1.2_full_instance_inverseRelations_OWLNETS_NetworkxMultiDiGraph.gpickle_

### Node Labels and Node Types
* Download _nodeLabels_v3.0.0.tsv_ file with all node labels for the merged KG.
* Download _nodeTypes_v3.0.0.tsv_ file with node types for all nodes in the merged KG.

2. See [evaluation-scripts](https://github.com/sanyabt/np-kg/tree/main/evaluation-scripts) for examples of queries and path searches.

Note: The download link also contains the KGs as gpickle and ntriples files with the same nodes and edges that can be loaded for other applications.

### Loading NP-KG with GRAPE

The Graph Representation Learning library [GRAPE](https://github.com/AnacletoLAB/grape) provides efficient graph embeddings. To load NP-KG (version 3.0.0) in GRAPE, use the _from_csv_ function and TSV files mentioned above:

```
npkg = Graph.from_csv(
            node_path=<TSV node types filename>,
            node_list_node_types_column_number=1,
            nodes_column_number=0,
            node_list_separator='\t',
            node_list_header=True,
            edge_path=<TSV version of KG filename>,
            edge_list_separator='\t',
            edge_list_header=True,
            edge_list_edge_types_column_number=1,
            sources_column_number=0,
            destinations_column_number=2,
            weights_column_number=3,
            directed=True,
            verbose=True
        )
```

NP-KG (v1.0.1) can also be loaded with as below. See [NP-KG Grape Animation tutorial](https://github.com/sanyabt/np-kg/blob/main/resources/NPKG-Grape-Animation.ipynb) for details.

```python
pip install grape -U
from grape.datasets.zenodo import NPKG
graph = NPKG(directed=True)
graph
```

### If you are interested in constructing or extending NP-KG

See [wiki](https://github.com/sanyabt/np-kg/wiki) for details of data sources, construction, use cases, and evaluation.

Get In Touch
------------------------------------------------

Get in touch through GitHub issues, discussion, or [email](mailto:sbt12@pitt.edu)!


Related Work
------------------------------------------------
**NP-KG Publication**

Taneja SB, Callahan TJ, Paine MF, Kane-Gill SL, Kilicoglu H, Joachimiak MP, Boyce RD. Developing a Knowledge Graph Framework for Pharmacokinetic Natural Product-Drug Interactions. Journal of Biomedical Informatics. 2023. [DOI: doi.org/10.1016/j.jbi.2023.104341](https://doi.org/10.1016/j.jbi.2023.104341).

**AMIA Informatics Summit poster**

Taneja SB, Ndungu PW, Paine MF, Kane-Gill SL, Boyce RD. Relation Extraction from Biomedical Literature on Pharmacokinetic Natural Product-Drug Interactions. Poster presentation, AMIA Informatics Summit 2022; March 21-24, 2022.

**ISMB Conference Abstract and Related Files**

Taneja SB, Callahan TJ, Brochhausen M, Paine MF, Kane-Gill SL, Boyce RD. Designing potential extensions from G-SRS to ChEBI to identify natural product-drug interactions. Intelligent Systems for Molecular Biology/European Conference on Computational Biology (ISMB/ECCB), 2021. [https://doi.org/10.5281/zenodo.5736386](https://doi.org/10.5281/zenodo.5736386)


Cite this Work
------------------------------------------------
**Publication**

```
@article{taneja_developing_2023,
	title = {Developing a {Knowledge} {Graph} for {Pharmacokinetic} {Natural} {Product}-{Drug} {Interactions}},
	volume = {140},
	issn = {1532-0464},
	url = {https://www.sciencedirect.com/science/article/pii/S153204642300062X},
	doi = {10.1016/j.jbi.2023.104341},
	language = {en},
	urldate = {2023-03-23},
	journal = {Journal of Biomedical Informatics},
	author = {Taneja, Sanya B. and Callahan, Tiffany J. and Paine, Mary F. and Kane-Gill, Sandra L. and Kilicoglu, Halil and Joachimiak, Marcin P. and Boyce, Richard D.},
	year = {2023},
}
```

**Zenodo Dataset**

```
@dataset{taneja_sanya_bathla_2024_12536780,
  author       = {Taneja, Sanya Bathla},
  title        = {{NP-KG: Knowledge Graph for Natural Product-Drug 
                   Interactions}},
  month        = jun,
  year         = 2024,
  publisher    = {Zenodo},
  version      = {3.0.0},
  doi          = {10.5281/zenodo.12536780},
  url          = {https://doi.org/10.5281/zenodo.12536780}
}
```

Funding
------------------------------------------------
This work is supported by the National Institutes of Health National Center for Complementary and Integrative Health Grant U54 AT008909.
