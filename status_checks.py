from collections import Counter
from urllib.parse import urlencode, urlparse, parse_qs
import re

def is_large_file(resp):
    file_size = int(resp.raw_response.headers.get('Content-Length', 0))
    return file_size > 1024 * 1024 #Don't parse files that are too large

def is_low_info(words):
    return not words or (len(words) < 100) #Change back to 50?

def remove_traps(base):
    parsed_base = urlparse(base)
    query_params = parse_qs(parsed_base.query)
    query_keys = list(query_params.keys())
    to_del = ["rev", "rev2", "do", "version", "v", "year", "month", "day", "date", "tribe-bar-date", "filter[units]"]
    for param in query_keys:
        if param in to_del or param.startswith("filter") or param.startswith("rev2"):
            del query_params[param]

    re_query = urlencode(query_params, doseq=True)
    new_url = parsed_base._replace(query=re_query).geturl().lower()

    return new_url

def handle_redirects(url, resp):
    return resp.headers['Location']


def detect_url_trap(url):
    parsed = urlparse(url)
    path = parsed.path
    
    # calendar trap
        # ignore calendars
    if re.search(r'/calendar/\d{4}/\d{2}/', path):
        return True
        
    # deep path
        # potentially recursive (inf) depth
    if path.count('/') > 10:
        return True
    
    # repeating pattern
    segments = path.split('/')
    if len(segments) > 3:
        segment_counter = Counter(segments)
        most_common = segment_counter.most_common(1)[0][1] # most common tuple (count)
        if most_common > 2:  # same segment appears more than twice
            return True
            
    # query parameter trap
        # too many urls or very long query strings.
    if len(parsed.query) > 100 or parsed.query.count('&') > 7:
        return True
        
    return False
    
