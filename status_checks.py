def is_large_file(resp):
    file_size = int(resp.raw_response.headers.get('Content-Length', 0))
    return file_size > 1024 * 1024 #Don't parse files that are too large

def is_low_info(words):
    return not words or (len(words) < 50)