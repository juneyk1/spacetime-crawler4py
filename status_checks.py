from urllib.parse import urlencode, urlparse, parse_qs

def is_large_file(resp):
    file_size = int(resp.raw_response.headers.get('Content-Length', 0))
    return file_size > 1024 * 1024 #Don't parse files that are too large

def is_low_info(words):
    return not words or (len(words) < 50)

def remove_traps(base):
    parsed_base = urlparse(base)
    query_params = parse_qs(parsed_base.query)
    query_keys = list(query_params.keys())
    to_del = ["rev", "version", "v", "year", "month", "day", "date", "tribe-bar-date", "filter[units]"]
    for param in query_keys:
        if param in to_del or param.startswith("filter"):
            del query_params[param]

    re_query = urlencode(query_params, doseq=True)
    new_url = parsed_base._replace(query=re_query).geturl().lower()

    return new_url

