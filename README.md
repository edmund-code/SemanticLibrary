# SemanticLibrary
Semantic Paper Map
Project Overview
This tool generates a visual conceptual landscape of a local research library. Unlike citation-based discovery tools, it uses Natural Language Processing and Vector Embeddings to map papers based on their actual content and thematic similarity.

Core Functionality
Text Extraction: Parses local PDF files to retrieve abstracts or body text.

Semantic Embedding: Converts text into high-dimensional vectors using Large Language Models.

Dimensionality Reduction: Projects high-dimensional data into a 2D or 3D coordinate system using UMAP or t-SNE.

Interactive Mapping: Produces a browser-based plot where users can explore clusters of related research.

Technical Stack
Language: Python

NLP: Sentence-Transformers (HuggingFace)

Processing: Scikit-learn, NumPy, Pandas

Visualization: Plotly, Dash

PDF Handling: PyMuPDF (Fitz)

How It Works
Preprocessing: The system reads a directory of PDFs and extracts the text content.

Vectorization: An embedding model assigns a numerical vector to each paper representing its meaning.

Clustering: Mathematical algorithms identify neighborhoods of similar papers.

Visualization: The data is rendered as an interactive scatter plot where proximity indicates semantic relevance.
