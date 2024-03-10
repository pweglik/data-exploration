import os
import time

import requests

# https://metacyc.org/cross-org-search?terms=&disjunctp=or&SearchFields=names&SearchFields=summary&types=pathways&resultsCount=1000&orgids=%28%29&sort=score+desc


def get_html_parameterized(
        terms="",
        disjunctp="or",
        search_fields=["names"],
        types="pathways",
        results_count=10,
        orgids="()",
        sort="score desc",
        start=0
):
    base_url = 'http://metacyc.org/cross-org-search'
    params = {
        "terms": terms,
        "disjunctp": disjunctp,
        "SearchFields": search_fields,
        "types": types,
        "resultsCount": results_count,
        "orgids": orgids,
        "sort": sort,
        "start": start
    }

    response = requests.get(base_url, params=params, timeout=120)

    return response.content


if __name__ == '__main__':
    step = 1000
    total = 5_000_000

    for i in range(0, total, step):
        name = f"metacyc_htmls/pathways_{i:07d}+{1000}.html"
        if os.path.exists(name):
            continue

        print(f"Feching {name}")
        t1 = time.time()
        try:
            html_content = get_html_parameterized(start=i, results_count=step)
        except Exception as e:
            print(f"Error: {e}")
            continue
        t2 = time.time()
        print(f"Time: {t2 - t1:.2f} seconds")

        with open(name, 'wb') as f:
            f.write(html_content)
