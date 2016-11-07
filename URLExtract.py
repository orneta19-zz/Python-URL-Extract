import concurrent.futures
import requests
import lxml.etree
from cStringIO import StringIO
import json

URLS = []
with open('/home/neta/PycharmProjects/getRss/urls', 'r') as f:
    URLS = f.readlines()

# Retrieve a single page and report the url and contents
def load_url(url, timeout):
    xpaths = ['//link[contains(@class, "youtube")]']
    r = requests.get(url.strip(), timeout=timeout, verify=False)
    body = r.content
    selectors = []
    element_tree = lxml.etree.parse(StringIO(body), lxml.etree.HTMLParser())
    for xpath in xpaths:
        selectors.extend(element_tree.xpath(xpath))

    results = []

    for res in selectors:
        results({'link':res.get('href')})

    results = {v['link']:v for v in results}.values()
    with open('/home/neta/PycharmProjects/getRss/rss_out', 'a') as f:
       f.write(json.dumps({"page": url.strip(), 'data': results}) + '\n')


# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
