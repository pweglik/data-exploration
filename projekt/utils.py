import numpy as np
from scipy.cluster.hierarchy import dendrogram


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


import requests
from bs4 import BeautifulSoup


def scrape_org_taxonomy(url):
    # Replace with your actual URL

    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, "html.parser")

    # Find the main content by id
    main_content = soup.find(id="mainContent")

    # Get organism name
    organism_name = main_content.find("i").text

    # Get taxonomic lineage. It seems each link with class 'ORGANISM' is an item in the lineage
    taxonomy_items = main_content.find_all("a", class_="ORGANISM")

    # Extract the text from each item
    taxonomy_lineage = [item.text for item in taxonomy_items if item.text != ","]

    return organism_name, taxonomy_lineage
