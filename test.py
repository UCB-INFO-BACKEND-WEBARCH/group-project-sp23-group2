import argparse
from urllib.parse import urljoin
import requests


def make_request_request(api_url,query):
    full_url = urljoin(api_url, "/message")
    print(full_url)
    raw_data = dict()
    
    try: 
        r = requests.post(full_url, json=raw_data)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as err:
        # eg, no internet
        raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        # eg, url, server and other errors
        raise SystemExit(err)

    data = r.json()

    return data["data"]