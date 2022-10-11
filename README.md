[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6814507.svg)](https://doi.org/10.5281/zenodo.6814507)

# NP-KG

**Knowledge Graph Framework to Generate Hypotheses for Natural Product-Drug Interactions**

![KG-Framework](images/methods-overview.png)

NP-KG is a graph framework that creates a biomedical knowledge graph (KG) to identify and generate mechanistic hypotheses for pharmacokinetic natural product-drug interactions (NPDIs). NP-KG uses the [PheKnowLator ecosystem](https://github.com/callahantiff/PheKnowLator) to create an ontology-grounded KG. It then uses two relation extraction systems to extract triples from natural product-related biomedical literature to create a literature-based graph, and integrates the nodes and edges in the ontology-grounded KG. 

## NP-KG Builds

**NP-KG:** Merged PheKnowLator KG and literature-based graph with green tea and kratom literature.

**Ontology-grounded KG:** PheKnowLator KG with a few [additional data sources](#).

**Literature-based Graph:** Literature-based graph constructed from green tea and kratom literature with relation extraction systems (SemRep and INDRA/REACH) and closure operations.

## How to Download and Use

### Setup environment

1. Clone the repository or download all files.
2. Install all required packages. Requires Python>=3.6.

```
python -m pip install -r requirements.txt
```

### If you want to use the pre-built KGs

1. [Download the knowledge graph and node labels files from Zenodo](https://doi.org/10.5281/zenodo.6814507) and add to local folder - resources/knowledge_graphs. NP-KG is available as NetworkX multidigraph (gpickle files) and triples (ntriples files).

* **Merged KG:** includes merged PheKnowLator KG and literature-based graph. Download this file if you do not know which KG to use.
	* Filename: _PheKnowLator_machine_read_merged_instance_based_OWLNETS_v1.0.1.tsv_
* **PheKnowLator KG:** includes full instance-based build of the PheKnowLator KG. See [PheKnowLator](https://github.com/callahantiff/PheKnowLator) for more details.
	* Filename: _PheKnowLator_v3.0.0_full_instance_inverseRelations_OWLNETS_NetworkxMultiDiGraph.gpickle_
* **Literature-based graph:** includes all nodes and edges extracted from full texts of green tea and kratom literature and inferred edges.
	* Filename: _machine_read_merged_with_closure_v1.0.pickle_

### Node Labels
* Download _nodeLabels_v1.0.1.tsv_ file with all node labels for the merged KG.

2. See [evaluation-scripts](https://github.com/sanyabt/np-kg/tree/main/evaluation-scripts) for examples of queries and path searches.

Note: The download link also contains the KGs as gpickle and ntriples files with the same nodes and edges that can be loaded for other applications.

### Loading NP-KG with GRAPE

NP-KG can also be loaded with the Graph Representation Learning library [GRAPE](https://github.com/AnacletoLAB/grape) for embedding and knowledge graph applications as below. See [NP-KG Grape Animation tutorial](https://github.com/sanyabt/np-kg/blob/main/resources/NPKG-Grape-Animation.ipynb) for example.

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
**NP-KG Preprint**

Taneja SB, Callahan TJ, Paine MF, Kane-Gill SL, Kilicoglu H, Joachimiak MP, Boyce RD. Developing a Knowledge Graph Framework for Pharmacokinetic Natural Product-Drug Interactions. arXiv. 2022. [10.48550/arXiv.2209.11950](https://doi.org/10.48550/arXiv.2209.11950).

**AMIA Informatics Summit poster**

Taneja SB, Ndungu PW, Paine MF, Kane-Gill SL, Boyce RD. Relation Extraction from Biomedical Literature on Pharmacokinetic Natural Product-Drug Interactions. Poster presentation, AMIA Informatics Summit 2022; March 21-24, 2022.

**ISMB Conference Abstract and Related Files**

Taneja SB, Callahan TJ, Brochhausen M, Paine MF, Kane-Gill SL, Boyce RD. Designing potential extensions from G-SRS to ChEBI to identify natural product-drug interactions. Intelligent Systems for Molecular Biology/European Conference on Computational Biology (ISMB/ECCB), 2021. [https://doi.org/10.5281/zenodo.5736386](https://doi.org/10.5281/zenodo.5736386)


Cite this Work
------------------------------------------------
**Preprint**
```
@misc{https://doi.org/10.48550/arxiv.2209.11950,
  doi		= {10.48550/ARXIV.2209.11950},
  url		= {https://arxiv.org/abs/2209.11950},
  author	= {Taneja, Sanya B. and Callahan, Tiffany J. and Paine, Mary F. and Kane-Gill, Sandra L. and Kilicoglu, Halil and Joachimiak, Marcin P. and Boyce, Richard D.},
  keywords	= {Artificial Intelligence (cs.AI), Quantitative Methods (q-bio.QM), FOS: Computer and information sciences, FOS: Computer and information sciences, FOS: Biological sciences, FOS: Biological sciences},
  title		= {Developing a Knowledge Graph Framework for Pharmacokinetic Natural Product-Drug Interactions},
  publisher	= {arXiv},
  year		= {2022},
  copyright	= {Creative Commons Attribution 4.0 International}
}
```

**Zenodo Dataset**

```
@dataset{taneja_sanya_bathla_2022_6814507,
  author       = {Taneja, Sanya Bathla},
  title        = {{NP-KG: Knowledge Graph Framework for Natural 
                   Product-Drug Interactions}},
  month        = aug,
  year         = 2022,
  note         = {{Supporting Grant - National Institutes of Health 
                   National Center for Complementary and Integrative
                   Health Grant U54 AT008909}},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.6814507},
  url          = {https://doi.org/10.5281/zenodo.6814507}
}
```

Funding
------------------------------------------------
This work is supported by the National Institutes of Health National Center for Complementary and Integrative Health Grant U54 AT008909.
