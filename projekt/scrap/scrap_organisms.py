import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm
import time

def scrape_metacyc(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extracting the display name
    display_name = soup.find('center', class_='header pageTitle').text.strip()
    
    # Extracting synonyms
    synonyms_paragraph = soup.find('p', class_='ecoparagraph', string=lambda t: t and 'Synonyms:' in t)
    synonyms = synonyms_paragraph.text.split('Synonyms: ')[1].strip() if synonyms_paragraph else 'No synonyms found'
    
    # Extracting NCBI Taxonomy IDs and their corresponding ranks
    taxonomy_data = []
    for link in soup.findAll('a', class_='ORGANISM'):
        if 'data-tippy-content' in link.attrs:
            tippy_content = BeautifulSoup(link['data-tippy-content'], 'html.parser').get_text()
            ncbi_id = tippy_content.split('NCBI Taxonomy ID: ')[1].split('Rank:')[0].strip()
            rank = tippy_content.split('Rank: ')[1].split('Lineage:')[0].strip()
            taxonomy_data.append({'Taxonomic Rank': rank, 'NCBI Taxonomy ID': ncbi_id})

    return {
        'Display Name': display_name,
        'Synonyms': synonyms,
        'Taxonomy': taxonomy_data
    }


queries = pd.read_csv("orgs.csv", header=None).values.flatten()
success = []
fail = []
for query in tqdm(queries):
    url = f"https://metacyc.org/META/NEW-IMAGE?type=NIL&object={query}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"{response.status_code} for {url}")
        fail.append(query)
        continue
    html_content = response.content
        
    with open(f"./htmls/{query}.html", 'w', encoding='utf-8') as file:
        file.write(html_content.decode())

    try:
        result = scrape_metacyc(html_content)
    
        with open(f"./jsons/{query}.json", 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)

        success.append(query)
        #print(f'Data saved for {query}')
    except Exception as e:
        print(f"error scraping {url}: {e}")
        fail.append(query)

    time.sleep(5)
