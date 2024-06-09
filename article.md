# Proposing new phylogenetic tree based on metabolic pathways

### Introduction on taxonomic trees
Classical taxonomic trees, also known as hierarchical classifications, have long been used by biologists to organize and categorize the vast diversity of life on Earth. These trees arrange organisms into nested categories such as kingdom, phylum, class, order, family, genus, and species based on shared physical characteristics and traits. This system provides a clear, structured way to identify and classify organisms, facilitating communication and study within the biological sciences.

However, while classical taxonomic trees are useful for organization and identification, they fall short in illustrating the evolutionary relationships among species. This is where phylogenetic trees come into play. A phylogenetic tree, or evolutionary tree, represents the evolutionary pathways and connections among various species based on genetic information and historical data. Unlike classical hierarchies, phylogenetic trees highlight the shared ancestry and divergence of species over time.

The primary difference between these two approaches lies in their focus and structure. Classical hierarchies emphasize a static arrangement based on morphological traits, without necessarily conveying evolutionary history. In contrast, phylogenetic trees dynamically depict the branching patterns of evolution, showing how species have evolved from common ancestors and diverged over time.

### Metabolic pathways

Metabolic pathways, also known as metabolic pathways, are sequences of chemical reactions that occur within a cell. These reactions are facilitated by enzymes and are crucial for various cellular processes, including energy production, synthesis of biomolecules, and regulation of cellular activities. Metabolic pathways are highly conserved across different species, meaning that many of the same pathways are found in a wide range of organisms, from bacteria to humans.

The study of metabolic pathways can provide valuable insights into the evolutionary relationships among species. By comparing the presence, absence, and variation of specific metabolic pathways in different organisms, scientists can infer patterns of evolutionary change and shared ancestry. These comparisons can be used to construct phylogenetic trees, which map out the evolutionary connections based on the similarities and differences in the metabolic networks of different species.

Comparative analysis of metabolic pathways in different organisms can give insights into the understanding of evolutionary and organizational relationships among species. This type of analysis allows one to measure the evolution of complete processes (with different functional roles) rather than the individual elements of a conventional analysis.

### Dataset

In our research we are going to use MetaCyc database. MetaCyc is a comprehensive database of metabolic pathways and enzymes from all domains of life, including bacteria, archaea, and eukaryotes. MetaCyc includes a vast collection of experimentally verified metabolic pathways. These pathways cover a wide array of biological processes, from primary metabolism (such as glycolysis and the citric acid cycle) to secondary metabolism (such as the biosynthesis of antibiotics and other specialized compounds).

### Solution

Our solution revolved around extracting data from Metacyc database. We were mainly interested in all metabolic pathways (and therefore chemical reactions) occuring in some subset of organisms. From those reactions we build graphs representing organisms. Verticies of these graphs are chemical compounds and edges are reactions transforming one compound into another. For simplicity we drop some of the most often occuring compounds like water or CO<sup>2</sup> (TODO VERIFY).
There was plenty of organisms that did not have enough reactions matched with them in a database, so we defined a well represented organism as sush that would have at least 100 reactions (TODO - VERIFY) and we only performed our further analysis on such organisms.

Our first step was to construct graphs representing organisms. After the graphs were cleaned, we needed a way to compare them, and for that you need some form of vector embedding. (TODO - VERIFY) The simplest method is to use one hot encoding on verticies of the graph. We construct list of all compounds occuring in all of graphs we are going to analyse. Then we construct vectors of length equal to the size of such dictionary. The vector, embedding an organism, will have 1 in a place corresponding to some compound, if this compund is present in this organism metabolic graph and 0 otherwise.

More interesting way to create embeddings is to use LTP or LDP (TODO - verify - writeup)

After creating vector representations for organisms we cluster them using hierarchical clustering. We want organisms with similar representation close in the hierarchy. We're nor particulary interested in clusters per se, but rather in entire tree hierarchy. Based on in, we can propose new ways of assiging organisms to taxonomical units.

### Results

TODO