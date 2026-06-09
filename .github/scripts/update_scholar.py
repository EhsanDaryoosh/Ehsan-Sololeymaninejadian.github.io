from scholarly import ProxyGenerator

pg = ProxyGenerator()
# If you want to try free proxies built into the library:
pg.FreeProxies()
scholarly.use_proxy(pg)
from scholarly import scholarly
import json
from datetime import datetime
import os
import time  # Added for delay

def update_scholar_stats():
    try:
        print("Fetching author profile...")
        author = scholarly.search_author_id('CzDqC04AAAAJ')
        author = scholarly.fill(author)
        
        stats = {
            'citations': author['citedby'],
            'h_index': author['hindex'],
            'publications': len(author['publications']),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'recent_publications': []
        }
        
        publications = author['publications']
        # Sort by year descending
        publications.sort(key=lambda x: int(x['bib'].get('pub_year', '0')), reverse=True)
        
        # 🔥 FIX 1: Limit to the 5 most recent publications to avoid hitting rate limits
        MAX_PUBS = 5 
        recent_pubs = publications[:MAX_PUBS]
        
        print(f"Processing the top {len(recent_pubs)} recent publications...")
        
        for i, pub in enumerate(recent_pubs):
            print(f"[{i+1}/{len(recent_pubs)}] Fetching details...")
            
            try:
                filled_pub = scholarly.fill(pub)
            except Exception as fill_err:
                print(f"Warning: Failed to fetch details for a publication, skipping. Error: {fill_err}")
                continue
            
            # Try to get the abstract from different possible locations
            abstract = (filled_pub.get('bib', {}).get('abstract') or 
                        filled_pub.get('abstract') or 
                        filled_pub.get('summary', 'Abstract not available'))
            
            pub_data = {
                'title': filled_pub['bib'].get('title', 'Unknown Title'),
                'year': filled_pub['bib'].get('pub_year', 'Year Unknown'),
                'citation': filled_pub['bib'].get('citation', 'Citation not available'),
                'abstract': abstract,
                'url': filled_pub.get('pub_url', '#'),
                'authors': filled_pub['bib'].get('author', [])
            }
            
            print(f"Successfully processed: {pub_data['title']}")
            stats['recent_publications'].append(pub_data)
            
            # 🔥 FIX 2: Add a 5-second sleep between requests so Google doesn't block us immediately
            if i < len(recent_pubs) - 1:
                print("Sleeping for 5 seconds to avoid rate limits...")
                time.sleep(5)
            
        os.makedirs('assets/data', exist_ok=True)
        json_path = os.path.join(os.getcwd(), 'assets/data/scholar_stats.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
            
        print("\nSuccessfully updated scholar stats and publications")
        
    except Exception as e:
        print(f"Critical error updating scholar stats: {str(e)}")
        raise e

if __name__ == "__main__":
    update_scholar_stats()