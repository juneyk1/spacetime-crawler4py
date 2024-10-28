import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
from nltk.corpus import stopwords
import csv
import os
from datetime import datetime
import status_checks as status

# Define stop words to ignore
STOP_WORDS = set(stopwords.words('english')) #Stopwords from nltk

# Global trackers for report questions
all_urls = set() #Track ALL urls visited, regardless of status
visited_urls = set()  # Question 1: Track unique pages
longest_page = {
    'url': None,
    'word_count': 0
}  # Question 2: Track longest page
word_counter = Counter()  # Question 3: Track word frequencies
subdomain_counter = defaultdict(int)  # Question 4: Track subdomains

def scraper(url, resp):
    """Main function to process each page and extract valid links."""
    links = []
    if url not in all_urls:
        links = extract_next_links(url, resp)
    all_urls.add(url)
    #valid_links = [link for link in links if is_valid(link)]
    
    # Print current statistics periodically
    if len(visited_urls) % 50 == 0:  # Every 50 pages
        print("\n=== Current Statistics ===")
        print(f"Unique pages: {len(visited_urls)}")
        print(f"Longest page: {longest_page['url']} ({longest_page['word_count']} words)")
        print(f"Subdomains found: {len(subdomain_counter)}")
        print("Top 5 words so far:", word_counter.most_common(5))
        print("========================\n")
    
    return links

def extract_next_links(url, resp):
    """Extract links while tracking report metrics."""
    links = []
    
    if resp.status == 200:
        try:
            if(status.is_large_file(resp)):
                return []
            
            # Parse content
            soup = BeautifulSoup(resp.raw_response.content, 'lxml')
            
            # Remove scripts, styles, and other non-content elements
            for element in soup(['script', 'style', 'meta', 'link', 'noscript', 'header', 'footer', 'nav']):
                element.decompose()
            
            # Extract text and clean it
            text = soup.get_text()
            
            # More aggressive text cleaning
            # Convert to lowercase and split into words
            words = [word.lower() for word in re.findall(r"\b[\w']{2,}\b", text)]
            
            #Don't go any further if dead url
            if status.is_low_info(words):
                return []

            # Filter out stop words
            filtered_words = [word for word in words if word not in STOP_WORDS] #TODO stopped deletion of chars < 2 (keep digits!)
            
            # Track unique URL (Question 1)
            visited_urls.add(url)
            
            # Track subdomain (Question 4)
            parsed_url = urlparse(url)
            if "ics.uci.edu" in parsed_url.netloc:
                subdomain_counter[parsed_url.netloc] += 1
            
            # Update longest page (Question 2) - use original word count including stop words
            word_count = len(words)  # Use original words for length
            if word_count > longest_page['word_count']:
                longest_page.update({
                    'url': url,
                    'word_count': word_count
                })
                print(f"New longest page found: {url} with {word_count} words")
            
            # Update word frequencies (Question 3) - use filtered words
            word_counter.update(filtered_words)
            
            # Extract links
            for link in soup.find_all('a', href=True):
                abs_link = urljoin(url, link['href'])
                base, fragment = urldefrag(abs_link)
                normalized = urlparse(base).geturl().lower()
                if is_valid(normalized) and normalized not in links and normalized not in all_urls:
                    links.append(normalized)
                    
        except Exception as e:
            print(f"Error processing {url}: {e}")
    return links

def save_report_data():
    """Save the collected data into a report format."""
    try:
        # Create stats directory
        stats_dir = 'crawler_stats'
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = os.path.join(stats_dir, f'report_stats_{timestamp}.csv')
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Basic Stats
            writer.writerow(['Report Statistics'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Unique Pages', len(visited_urls)])
            writer.writerow(['Total Words Processed', sum(word_counter.values())])
            writer.writerow(['Total Subdomains Found', len(subdomain_counter)])
            writer.writerow([''])
            
            # Question 1: Unique Pages
            writer.writerow(['All Unique URLs'])
            for url in sorted(visited_urls):
                writer.writerow([url])
            writer.writerow([''])
            
            # Question 2: Longest Page
            writer.writerow(['Longest Page Details'])
            writer.writerow(['URL', longest_page['url']])
            writer.writerow(['Word Count', longest_page['word_count']])
            writer.writerow([''])
            
            # Question 3: Most Common Words (excluding stop words)
            writer.writerow(['50 Most Common Words (excluding stop words)'])
            writer.writerow(['Word', 'Frequency'])
            for word, count in word_counter.most_common(50):
                writer.writerow([word, count])
            writer.writerow([''])
            
            # Question 4: Subdomain Analysis
            writer.writerow(['Subdomains Found in ics.uci.edu'])
            writer.writerow(['Subdomain', 'Page Count'])
            for subdomain, count in sorted(subdomain_counter.items()):
                writer.writerow([subdomain, count])
                
        print(f"Report saved to {filename}")
        
    except Exception as e:
        print(f"Error saving report: {e}")

def is_valid(url):
    """Check if the URL should be crawled."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {'http', 'https'}:
            return False

        if not any(domain in parsed.netloc for domain in [
            "ics.uci.edu", 
            "cs.uci.edu", 
            "informatics.uci.edu", 
            "stat.uci.edu"
        ]):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|java)$", parsed.path.lower())

    except TypeError:
        print("TypeError on ", parsed)
        raise

