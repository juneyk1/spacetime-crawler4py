import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
import os
import hashlib

def scraper(url, resp):
    if resp.status == 200:
        save_page(url, resp.raw_response.content)
        links = extract_next_links(url, resp)
        return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    links = []
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if(resp.status == 200):
        #Add url --> save number of unique pages visited (make sure to remove fragment part)
        #Collect tokens --> frequency & total (HTML Markup doesn't count)
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        for link in soup.find_all('a', href = True):
            abs_link = urljoin(url, link['href'])
            base, fragment = urldefrag(abs_link)
            normalized = urlparse(base).geturl().lower()
            if is_valid(base) and normalized not in links:
                links.append(normalized)
                
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    valid_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu", "today.uci.edu/department/information_computer_sciences"]
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        domain = parsed.netloc
        if not any(domain.endswith(d) for d in valid_domains):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def save_page(url, content):
    save_dir = "crawled_pages"
    os.makedirs(save_dir, exist_ok=True)

    file_name = hashlib.md5(url.encode('utf-8')).hexdigest() + ".html"
    file_path = os.path.join(save_dir, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)