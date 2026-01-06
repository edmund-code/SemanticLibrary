import os
import webbrowser
import pandas as pd
import xml.etree.ElementTree as ET
import networkx as nx
from grobid_client.grobid_client import GrobidClient
from pyvis.network import Network

def extract_metadata_and_refs(pdf_folder):
    xml_folder = os.path.join(os.path.dirname(pdf_folder), "Extracted_XML")
    if not os.path.exists(xml_folder):
        os.makedirs(xml_folder)

    client = GrobidClient(config_path=None, check_server=True)
    print(f"Processing PDFs from {pdf_folder}...")
    # Force=False ensures we don't re-process files you already have
    # consolidate_header=1 fetches official metadata to fix "wrong" XML info
    client.process("processFulltextDocument", pdf_folder, output=xml_folder, consolidate_header=1, generateIDs=False, force=False)
    
    data = []
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    for filename in os.listdir(xml_folder):
        if not filename.endswith('.grobid.tei.xml'): continue
        file_path = os.path.join(xml_folder, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 1. Title
            title_node = root.find(".//tei:titleStmt/tei:title", ns)
            title = title_node.text if title_node is not None else filename
            
            # 2. Year
            date_node = root.find(".//tei:publicationStmt/tei:date", ns)
            year = date_node.get('when')[:4] if date_node is not None and date_node.get('when') else "N/A"
            
            # 3. Full Author List
            author_list = []
            for author in root.findall(".//tei:sourceDesc//tei:author", ns):
                persName = author.find("tei:persName", ns)
                if persName is not None:
                    forename = persName.find("tei:forename", ns)
                    surname = persName.find("tei:surname", ns)
                    f_name = forename.text if forename is not None else ""
                    s_name = surname.text if surname is not None else ""
                    full_name = f"{f_name} {s_name}".strip()
                    if full_name:
                        author_list.append(full_name)
            
            primary_author = author_list[0].split()[-1] if author_list else "Unknown"
            full_authors_str = ", ".join(author_list) if author_list else "Unknown"
            
            # 4. Robust Abstract Extraction
            abstract_node = root.find(".//tei:abstract", ns)
            abstract = ""
            if abstract_node is not None:
                # Try to get paragraphs first
                paragraphs = abstract_node.findall(".//tei:p", ns)
                if paragraphs:
                    abstract = " ".join(["".join(p.itertext()).strip() for p in paragraphs])
                else:
                    # Fallback: Get all text in the abstract node if no <p> tags exist
                    abstract = "".join(abstract_node.itertext()).strip()
                
                # Clean up: Remove leading GitHub links or common "noise" patterns
                if abstract.lower().startswith("http") or "figure" in abstract[:50].lower():
                    # If the first 'sentence' looks like a link or figure, try to skip it
                    parts = abstract.split(". ", 1)
                    if len(parts) > 1:
                        abstract = parts[1]

            if not abstract:
                abstract = "No abstract available."
            
            # 5. References
            refs = [t.text.lower().strip() for t in root.findall(".//tei:listBibl//tei:title", ns) if t.text]
            
            data.append({
                "title": title, "year": year, "primary_author": primary_author, 
                "full_authors": full_authors_str, "abstract": abstract, 
                "refs": set(refs), "filename": filename
            })
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    return pd.DataFrame(data)

def build_connected_graph(df):
    G = nx.Graph()
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            shared_refs = df.iloc[i]['refs'].intersection(df.iloc[j]['refs'])
            if len(shared_refs) > 0:
                G.add_edge(i, j, weight=len(shared_refs))

    net = Network(height="100vh", width="100%", bgcolor="#ffffff", font_color="#343434", notebook=False)
    
    for idx, row in df.iterrows():
        degree = G.degree(idx) if idx in G else 0
        node_size = 15 + (degree * 3)
        
        net.add_node(idx, 
                   label=" ".join(str(row['title']).split()[:4]), 
                   size=node_size, 
                   color='#4d8d8c',
                   custom_title=row['title'],
                   custom_author=row['full_authors'], # Now passing full list
                   custom_year=row['year'],
                   custom_abstract=row['abstract'])

    for e in G.edges(data=True):
        net.add_edge(e[0], e[1], value=e[2]['weight'], color='#cbd5e0', opacity=0.4)

    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -150,
          "centralGravity": 0.005,
          "springLength": 200,
          "avoidOverlap": 1
        },
        "solver": "forceAtlas2Based",
        "stabilization": {
          "enabled": true,
          "iterations": 1000,
          "updateInterval": 25,
          "onlyDynamicEdges": false,
          "fit": true
        }
      },
      "interaction": {
        "hover": true,
        "dragNodes": true,
        "hideEdgesOnDrag": false,
        "hideNodesOnDrag": false
      },
      "nodes": {
        "font": {
          "size": 40
        }
      }
    }
    
    """)

    output_path = "connected_papers_sidebar.html"
    net.save_graph(output_path)

    # Logic to build the list of papers for the left sidebar
    paper_list_items = ""
    for idx, row in df.iterrows():
        paper_list_items += f"<div style='padding:10px; border-bottom:1px solid #eee; font-size:0.9em; color:#444;'>{row['title']}</div>"

    sidebar_html = f"""
    <div id="left-sidebar" style="position:fixed; left:0; top:0; width:300px; height:100%; background:#f8f9fa; border-right:1px solid #ddd; padding:20px; overflow-y:auto; z-index:1000; font-family: sans-serif;">
        <h3 style="font-size: 1.1em; margin-bottom: 15px; color: #333;">All Papers ({len(df)})</h3>
        <div id="paper-list">
            {paper_list_items}
        </div>
    </div>

    <div id="right-sidebar" style="position:fixed; right:0; top:0; width:400px; height:100%; background:white; border-left:1px solid #ddd; padding:25px; overflow-y:auto; z-index:1000; font-family: sans-serif; box-shadow: -2px 0 10px rgba(0,0,0,0.05);">
        <h2 id="s_title" style="font-size: 1.2em; color: #333; margin-bottom:10px;">Hover over a node</h2>
        <div style="margin-bottom: 15px;">
            <p style="color: #333; font-weight: bold; margin-bottom: 5px;">Authors:</p>
            <p id="s_author" style="color: #666; font-size: 0.95em; line-height: 1.4;">-</p>
        </div>
        <p style="color: #666; font-size: 0.95em;"><strong style="color: #333;">Year:</strong> <span id="s_year">-</span></p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p id="s_abstract" style="font-size: 1em; line-height: 1.6; color: #444; white-space: pre-wrap;">Abstract will appear here.</p>
    </div>

    <script>
        // Use double braces {{ }} so Python f-string doesn't crash
        network.on("stabilizationIterationsDone", function () {{
            network.setOptions({{ physics: false }});
        }});
        
        network.on("hoverNode", function (params) {{
            var nodeData = nodes.get(params.node);
            document.getElementById("s_title").innerText = nodeData.custom_title;
            document.getElementById("s_author").innerText = nodeData.custom_author;
            document.getElementById("s_year").innerText = nodeData.custom_year;
            document.getElementById("s_abstract").innerText = nodeData.custom_abstract;
        }});
    </script>
    """
    
    with open(output_path, "a") as f:
        f.write(sidebar_html)

    webbrowser.open(f'file://{os.path.abspath(output_path)}')

if __name__ == "__main__":
    pdf_folder = "/Users/edmundtsou/Desktop/SemanticLibrary/Papers"
    df = extract_metadata_and_refs(pdf_folder)
    if not df.empty:
        build_connected_graph(df)