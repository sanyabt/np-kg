[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6814508.svg)](https://doi.org/10.5281/zenodo.6814508)

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
2. Install all required packages. Requires Python==3.6 or above.

```
python -m pip install -r requirements.txt
```

### If you want to use the pre-built KGs

1. [Download the knowledge graph and node labels files from Zenodo](https://doi.org/10.5281/zenodo.6814508) and add to local folder - resources/knowledge_graphs. NP-KG is available as NetworkX multidigraph (gpickle files) and triples (ntriples files).

* **Merged KG:** includes merged PheKnowLator KG and literature-based graph. Download this file if you do not know which KG to use.
	* Filename: _PheKnowLator_machine_read_merged_instance_based_OWLNETS_v1.0.gpickle_
* **PheKnowLator KG:** includes full instance-based build of the PheKnowLator KG. See [PheKnowLator](https://github.com/callahantiff/PheKnowLator) for more details.
	* Filename: _PheKnowLator_v3.0.0_full_instance_inverseRelations_OWLNETS_NetworkxMultiDiGraph.gpickle_
* **Literature-based graph:** includes all nodes and edges extracted from full texts of green tea and kratom literature and inferred edges.
	* Filename: _machine_read_merged_with_closure_v1.0.pickle_
* **Node Labels:** pickle file with all node labels for the merged KG.
	* Filename: _nodeLabels_v1.0.pickle_

2. See [evaluation-scripts](https://github.com/sanyabt/np-kg/tree/main/evaluation-scripts) for examples of queries and path searches.

Note: The download link also contains the KGs as ntriples files with the same nodes and edges that can be loaded for other applications.


### If you are interested in constructing or extending NP-KG

See [wiki](https://github.com/sanyabt/np-kg/wiki) for details of data sources, construction, use cases, and evaluation.

Get In Touch
------------------------------------------------

Get in touch through GitHub issues, discussion, or [email](mailto:sbt12@pitt.edu)!


Related Work
------------------------------------------------

**AMIA Informatics Summit poster**

Taneja SB, Ndungu PW, Paine MF, Kane-Gill SL, Boyce RD. Relation Extraction from Biomedical Literature on Pharmacokinetic Natural Product-Drug Interactions. Poster presentation, AMIA Informatics Summit 2022; March 21-24, 2022.

**ISMB Conference Abstract and Related Files**

Taneja SB, Callahan TJ, Brochhausen M, Paine MF, Kane-Gill SL, Boyce RD. Designing potential extensions from G-SRS to ChEBI to identify natural product-drug interactions. Intelligent Systems for Molecular Biology/European Conference on Computational Biology (ISMB/ECCB), 2021. [https://doi.org/10.5281/zenodo.5736386](https://doi.org/10.5281/zenodo.5736386)


Cite this Work
------------------------------------------------
**Zenodo**

```
@dataset{taneja_sanya_bathla_2022_6814508,
  author       = {Taneja, Sanya Bathla},
  title        = {{NP-KG: Knowledge Graph Framework for Natural 
                   Product-Drug Interactions}},
  month        = aug,
  year         = 2022,
  note         = {{Supporting Grant - National Institutes of Health 
                   National Center for Complementary and Integrative
                   Health Grant U54 AT008909}},
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.6814508},
  url          = {https://doi.org/10.5281/zenodo.6814508}
}
```

This work is supported by the National Institutes of Health National Center for Complementary and Integrative Health Grant U54 AT008909.
