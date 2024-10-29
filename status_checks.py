from urllib.parse import urlparse
from collections import Counter
import re

def is_large_file(resp):
    file_size = int(resp.raw_response.headers.get('Content-Length', 0))
    return file_size > 1024 * 1024 #Don't parse files that are too large

def is_low_info(words):
    return not words or (len(words) < 50)

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

    #sources:
    # https://en.wikipedia.org/wiki/Spider_trap
    # https://www.conductor.com/academy/crawler-traps/#common-crawler-traps-and-how-to-avoid-them