from utils import get_logger 
from collections import Counter 
from bs4 import BeautifulSoup
import re
"""
This class is responsible for tracking unique URLS, word frequencies, and page analytics.
"""
class CrawlerTracker:
    
    def __init__(self):
        self.logger = get_logger("CrawlerTracker")
        self.word_counter = Counter()
        self.visited_urls = set()
        self.longest_page = { 'url': None, 'word_count': 0}

    def track_visit(self, url, resp):
        if url not in self.visited_urls:
            self.visited_urls.add(url)
            self.logger.info(f"New unique URL discovered: {url}")
        self.logger.info(f"Response status for {url}: {resp.status}")

    def track_words(self, url, soup):
        try:
            text = soup.get_text()
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = len(words)
            if word_count > self.longest_page['word_count']:
                self.longest_page = {'url': url, 'word_count': word_count}
                self.logger.info(f"New longest page: {url} with {word_count} words")
            self.word_counter.update(words)
        except Exception as e:
            self.logger.error(f"Error tracking words for {url}: {e}")
        
    def get_statistics(self):
        stats = {'unique_pages': len(self.visited_urls),
            'longest_page': self.longest_page,
            'most_common_words': self.word_counter.most_common(50)}
        
        self.logger.info("=== Crawler Statistics ===")
        self.logger.info(f"Total unique pages: {stats['unique_pages']}")
        self.logger.info(f"Longest page: {self.longest_page['url']} ({self.longest_page['word_count']} words)")
        self.logger.info("\n3. 50 most common words:")
        for word, count in stats['most_common_words']:
            self.logger.info(f"  {word}: {count}")
        return stats