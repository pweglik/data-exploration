import numpy as np
import pandas as pd
from typing import List, Union

from data_utils import read_pathways, read_reactions, read_compounds

pathways_df = read_pathways()
reactions_df = read_reactions()
compounds_df = read_compounds()

class Graph:
    def __new__(cls, adj_matrix: np.array, reactions: List[str], compounds: List[str]):
        graph = super().__new__(cls)
        graph.adj_matrix = adj_matrix
        graph.reactions = reactions
        graph.compounds = compounds
        return graph
        
    def __init__(self, id: Union[str, List[str]]):
        pass
    
    @staticmethod
    def from_reactions(reaction_ids: List[str], include_reactions:bool=True):
        edges, compound_v, reaction_v = set(), set(), set()

        reactions = reactions_df.loc[reaction_ids]
        if include_reactions:
            for i, reaction in reactions.iterrows():
                reaction_v.add(i)
                for l in reaction["Left"]:
                    compound_v.add(l)
                    edges.add((l, i))
                for r in reaction["Right"]:
                    compound_v.add(r)
                    edges.add((i, r))
        else:
            for i, reaction in reactions.iterrows():
                for l in reaction["Left"]:
                    compound_v.add(l)
                    for r in reaction["Right"]:
                        compound_v.add(r)
                        edges.add((l, r))
        
        vertices = list(compound_v) + list(reaction_v)
        adj_matrix = np.zeros((len(vertices), len(vertices)))
        for edge in edges:
            adj_matrix[vertices.index(edge[0]), vertices.index(edge[1])] = 1

        return Graph.__new__(Graph, adj_matrix, list(reaction_v), list(compound_v))

    @staticmethod
    def from_pathways(pathway_ids: List[str], include_subpathways=True):
        pathways = pathways_df.loc[pathway_ids]
        reaction_ids = set.union(*(set(x) for x in pathways["Reaction-List"]))

        if include_subpathways and any("PWY" in r for r in reaction_ids):
            sub_pathway_ids = [r for r in reaction_ids if "PWY" in r]
            sub_pathways = pathways_df.loc[sub_pathway_ids]

            more_reaction_ids = set.union(*(set(x) for x in sub_pathways["Reaction-List"]))
            reaction_ids.update(more_reaction_ids)

        reaction_ids = [r for r in reaction_ids if "PWY" not in r]
        
        
        return Graph.from_reactions(reaction_ids)

    @staticmethod
    def from_organism(organism_id: str):
        pathways = pathways_df.index[
            pathways_df["Species"].map(lambda x: organism_id in x if type(x) == list else False)
        ]

        return Graph.from_pathways(list(pathways))

    def prune_compounds(self, to_remove: List[str]):
        all_labels = self.compounds + self.reactions
        indices_to_keep = [i for (i, x) in enumerate(all_labels) if x not in to_remove]
        
        adj_matrix = self.adj_matrix[indices_to_keep, :][:, indices_to_keep]
        reactions = [r for r in reactions if r not in to_remove]
        compounds = [c for c in compounds if c not in to_remove]
        
        return Graph.__new__(Graph, adj_matrix, reactions, compounds)
        
    def plot(self):
        node_labels = compounds + reactions
        G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)
        mapping = dict(zip(range(len(node_labels)), node_labels))
        G = nx.relabel_nodes(G, mapping)
        group_colors = ['lightblue'] * len(compounds) + ['lightgreen'] * len(reactions)
        plt.figure(figsize=(12, 10))
        pos = graphviz_layout(G, prog='dot')  
        nx.draw(G, pos, with_labels=True, node_color=group_colors, node_size=1000, edge_color='gray', linewidths=1, font_size=10)
        plt.title("Graph Representation of Reactions and Compounds")
        plt.show()