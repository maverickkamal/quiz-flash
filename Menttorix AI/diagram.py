import xml.etree.ElementTree as ET
import re
from langchain_core.tools import tool
from typing import Optional

class SVGDiagramGenerator:
    def __init__(self):
        self.svg = None
        self.nodes = {}
        self.width = 800
        self.height = 600
        self.node_width = 120
        self.node_height = 60
        self.margin = 40

    def create_svg_element(self):
        self.svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': str(self.width),
            'height': str(self.height),
            'viewBox': f'0 0 {self.width} {self.height}'
        })

    def add_node(self, id, label, x, y, shape='rect'):
        group = ET.SubElement(self.svg, 'g', {'id': id})
        if shape == 'rect':
            ET.SubElement(group, 'rect', {
                'x': str(x),
                'y': str(y),
                'width': str(self.node_width),
                'height': str(self.node_height),
                'rx': '5',
                'ry': '5',
                'fill': 'lightblue',
                'stroke': 'navy',
                'stroke-width': '2'
            })
        elif shape == 'diamond':
            points = f"{x},{y+self.node_height/2} {x+self.node_width/2},{y} {x+self.node_width},{y+self.node_height/2} {x+self.node_width/2},{y+self.node_height}"
            ET.SubElement(group, 'polygon', {
                'points': points,
                'fill': 'lightgreen',
                'stroke': 'green',
                'stroke-width': '2'
            })
        
        text = ET.SubElement(group, 'text', {
            'x': str(x + self.node_width / 2),
            'y': str(y + self.node_height / 2),
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'fill': 'black'
        })
        text.text = label
        
        self.nodes[id] = (x + self.node_width / 2, y + self.node_height / 2)

    def add_edge(self, from_id, to_id, label=None):
        start = self.nodes[from_id]
        end = self.nodes[to_id]
        
        path = ET.SubElement(self.svg, 'path', {
            'd': f'M{start[0]},{start[1]} L{end[0]},{end[1]}',
            'fill': 'none',
            'stroke': 'navy',
            'stroke-width': '2',
            'marker-end': 'url(#arrowhead)'
        })
        
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            text = ET.SubElement(self.svg, 'text', {
                'x': str(mid_x),
                'y': str(mid_y),
                'text-anchor': 'middle',
                'dominant-baseline': 'middle',
                'fill': 'black'
            })
            text.text = label

    def create_diagram(self, description):
        self.create_svg_element()
        
        # Define arrow marker
        defs = ET.SubElement(self.svg, 'defs')
        marker = ET.SubElement(defs, 'marker', {
            'id': 'arrowhead',
            'markerWidth': '10',
            'markerHeight': '7',
            'refX': '9',
            'refY': '3.5',
            'orient': 'auto'
        })
        ET.SubElement(marker, 'polygon', {
            'points': '0 0, 10 3.5, 0 7',
            'fill': 'navy'
        })
        
        lines = description.strip().split('\n')
        nodes = [line for line in lines if '->' not in line]
        edges = [line for line in lines if '->' in line]
        
        # Position nodes in a grid layout
        cols = 3
        for i, node in enumerate(nodes):
            x = self.margin + (i % cols) * (self.node_width + self.margin)
            y = self.margin + (i // cols) * (self.node_height + self.margin)
            shape = 'diamond' if 'diamond' in node.lower() else 'rect'
            self.add_node(f'node{i}', node.strip(), x, y, shape)
        
        for edge in edges:
            from_node, to_node = edge.split('->')
            from_id = f'node{nodes.index(from_node.strip())}'
            to_id = f'node{nodes.index(to_node.strip())}'
            self.add_edge(from_id, to_id)

    def save(self, filename):
        tree = ET.ElementTree(self.svg)
        tree.write(filename, encoding='unicode', xml_declaration=True)
        return f"Diagram saved as {filename}"

generator = SVGDiagramGenerator()

@tool
def generate_svg_diagram(description: str, filename: Optional[str] = 'diagram.svg') -> str:
    """
    Generate an SVG diagram based on a text description.
    
    The description should contain node names (one per line) followed by edges (using -> notation).
    Example:
    Start
    Collect Data
    Analyze Data
    Decision
    End Process
    Start -> Collect Data
    Collect Data -> Analyze Data
    Analyze Data -> Decision
    Decision -> End Process
    Decision -> Collect Data
    
    Args:
        description (str): The text description of the diagram.
        filename (str, optional): The filename to save the SVG diagram. Defaults to 'diagram.svg'.
    
    Returns:
        str: A message indicating where the diagram was saved.
    """
    generator.create_diagram(description)
    return generator.save(filename)
