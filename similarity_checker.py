from collections import Counter
import math

def get_cosine_similarity(text1, text2):
    """Calculate cosine similarity between two texts"""
    # Get word vectors
    vector1 = Counter(text1)
    vector2 = Counter(text2)
    
    # Get intersection of words
    common_words = set(vector1.keys()) & set(vector2.keys())
    
    # Calculate dot product
    dot_product = sum(vector1[word] * vector2[word] for word in common_words)
    
    # Calculate magnitudes
    mag1 = math.sqrt(sum(count * count for count in vector1.values()))
    mag2 = math.sqrt(sum(count * count for count in vector2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    return dot_product / (mag1 * mag2)

class ContentTracker:
    def __init__(self):
        self.page_contents = {}  # url -> filtered_words mapping
        self.similar_pages = []  # list of (url1, url2, similarity_score)
    
    def add_page(self, url, filtered_words):
        """Add a page's content and check similarity with existing pages"""
        # Store new page content
        self.page_contents[url] = filtered_words
        
        # Compare with existing pages
        for existing_url, existing_words in self.page_contents.items():
            if existing_url != url:
                similarity = get_cosine_similarity(filtered_words, existing_words)
                if similarity > 0.8:  # High similarity threshold
                    self.similar_pages.append((url, existing_url, similarity))
                    print(f"\nFound similar content ({similarity:.2f}):")
                    print(f"Page 1: {url}")
                    print(f"Page 2: {existing_url}")