from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os
import sys

# Try setting up free proxies, but continue if it fails
try:
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    print("Proxy configuration initialized.")
except Exception as proxy_e:
    print(f"Proxy setup failed (falling back to direct connection): {proxy_e}")

def update_scholar_stats():
    try:
        print("Fetching Google Scholar Profile...")
        author = scholarly.search_author_id('CzDqC04AAAAJ')
        author = scholarly.fill(author)
        
        stats = {
            'citations': author.get('citedby', 0),
            'h_index': author.get('hindex', 0),
            'publications': len(author.get('publications', [])),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'recent_publications': []
        }
        
        publications = author.get('publications', [])
        # Sort publications by year descending
        publications.sort(key=lambda x: int(x['bib'].get('pub_year', '0')), reverse=True)
        
        # Limit to top 10 publications to keep file size small and execution fast
        recent_pubs = publications[:10]
        
        print(f"Processing data for {len(recent_pubs)} recent publications...")
        for pub in recent_pubs:
            # NOTICE: We are NOT calling scholarly.fill(pub) here anymore!
            # This completely avoids triggering Google's anti-bot system.
            bib = pub.get('bib', {})
            
            pub_data = {
                'title': bib.get('title', 'Unknown Title'),
                'year': bib.get('pub_year', 'Year Unknown'),
                'citation': bib.get('citation', 'Citation not available'),
                'abstract': bib.get('abstract', 'Abstract not available (Skipped to prevent rate-limiting)'),
                'url': pub.get('pub_url', '#'),
                'authors': bib.get('author', [])
            }
            stats['recent_publications'].append(pub_data)
            
        # Save JSON output
        os.makedirs('assets/data', exist_ok=True)
        json_path = os.path.join(os.getcwd(), 'assets/data/scholar_stats.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
            
        print("Successfully updated scholar_stats.json!")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        # Exit with a failure status code (1) so GitHub Actions knows it failed 
        # and doesn't push empty/corrupted code to your live site
        sys.exit(1) 

if __name__ == "__main__":
    update_scholar_stats()