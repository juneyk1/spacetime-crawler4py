from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from collections import defaultdict

class RobotHandler:

    """Cachce results based on domain/subdomain, to avoid repeatedly downloading robots.txt file.
        Robot Handler handles most of domain validation."""

    def __init__(self):
        self.robot_parsers = {}
        self.user_agent = "IR F19 uci-id1,uci-id2,uci-id3"

    def can_fetch(self, url):
        try:
            parsed = urlparse(url)
            domain = parsed.scheme + "://" + parsed.netloc # complete url
            
            # If we haven't checked this domain before
            if domain not in self.robot_parsers:
                rp = RobotFileParser()
                rp.set_url(domain + "/robots.txt")
                rp.read()
                # delay? - not sure if i need to set here.
                self.robot_parsers[domain] = rp 
            
            # Robot Parser does heavy work, of checking robots.txt rules
            return self.robot_parsers[domain].can_fetch(self.user_agent, url)
        except:
            # If anything goes wrong (can't fetch robots.txt, etc)
            return True  # assume it's OK to crawl if robots.txt is unavailable

# sources: 
# https://docs.python.org/3/library/urllib.robotparser.html
# https://docs.python.org/3/library/urllib.parse.html
