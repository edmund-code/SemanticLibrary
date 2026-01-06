# AcademicLibrary

A professional research tool for the local analysis and visualization of academic libraries. AcademicLibrary processes PDF documents to extract metadata and creates an interactive, force-directed network map based on bibliographic coupling.

## Overview

The application utilizes the GROBID (Geneva Reference Extraction from Bibliographic Information Document) server to parse full-text PDFs. It identifies shared references between documents to calculate a similarity metric, visually clustering related research while maintaining a local, private database.

## Core Features

### 1. Document Extraction
* Full-text parsing of academic PDFs using GROBID REST API.
* Metadata consolidation to verify titles, authors, and publication years against external records.
* Extraction of bibliography lists to enable similarity mapping.

### 2. Network Visualization
* Bibliographic Coupling: Nodes are connected based on shared citations in their respective bibliographies.
* Force-Directed Layout: Implementation of the ForceAtlas2 algorithm to distribute papers based on connection strength.
* Node Scaling: Geometric scaling of nodes according to their degree of connectivity within the local library.

### 3. Interactive UI
* Dual Sidebar Interface: A left-hand navigation pane for a full library list and a right-hand detail pane for metadata.
* Dynamic Detail View: Real-time updates of paper abstracts, full author lists, and years upon node hover.
* Stability Control: Automated physics stabilization that locks nodes in place once equilibrium is reached.

## Technical Stack

* **Processing Engine**: GROBID (Dockerized).
* **Network Analysis**: NetworkX.
* **Visualization Layer**: Pyvis (D3.js based).
* **Data Management**: Pandas.

## Implementation Details

### Similarity Logic
The relationship between two papers ($i$ and $j$) is determined by the intersection of their reference sets:
$$Strength = |Refs_i \cap Refs_j|$$
Connections are established for any non-zero intersection, pulling related papers into thematic clusters.

### Metadata Processing
The tool implements a caching mechanism to avoid redundant processing. Extracted XML files are stored in a separate directory (`Extracted_XML`), ensuring the original PDF folder remains organized.

## Setup Requirements

1. **Docker**: Ensure the GROBID server is running locally:
   `docker run -t --rm -p 8070:8070 grobid/grobid:0.8.0`
2. **Directory Structure**: Place all target PDFs in the designated `/Papers` directory.
3. **Dependencies**: Requires `grobid-client-python`, `pandas`, `networkx`, and `pyvis`.

## Usage

Execute the main application script:
`python app.py`

Upon completion, an interactive HTML file (`connected_papers_sidebar.html`) will be generated and automatically opened in the default system browser.
