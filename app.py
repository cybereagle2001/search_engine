from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse
import random
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 10
request_timestamps = []

# Search engines configuration
SEARCH_ENGINES = [
    {
        'name': 'Google',
        'url': 'https://www.google.com/search',
        'params': lambda query, page: {
            'q': query,
            'num': 10,
            'start': (page - 1) * 10
        }
    },
    {
    {
        'name': 'DuckDuckGo',
        'url': 'https://html.duckduckgo.com/html/',
        'params': lambda query, page: {
            'q': query,
            's': (page - 1) * 10
        }
    }
]

# Rotating User-Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
]

# Define trusted cybersecurity domains
TRUSTED_DOMAINS = {
    # News and Research
    'krebsonsecurity.com': 1.5,
    'darkreading.com': 1.5,
    'thehackernews.com': 1.5,
    'threatpost.com': 1.5,
    'bleepingcomputer.com': 1.5,
    'cisa.gov': 1.8,
    'sans.org': 1.7,
    'cybersecurityventures.com': 1.4,
    'nakedsecurity.sophos.com': 1.5,
    'zdnet.com': 1.3,
    'welivesecurity.com': 1.5,
    'recordedfuture.com': 1.5,
    'scmagazine.com': 1.4,
    'haveibeenpwned.com': 1.5,
    'attack.mitre.org': 1.8,
    'cve.mitre.org': 1.8,
    'cia.gov': 1.9,
    'nvd.nist.gov': 1.9,
    'us-cert.gov': 1.8,
    'nvd.nist.gov': 1.9,
    # Major Security Companies
    'crowdstrike.com': 1.6,
    'paloaltonetworks.com': 1.6,
    'fortinet.com': 1.6,
    'broadcom.com': 1.5,
    'checkpoint.com': 1.6,
    'mandiant.com': 1.7,
    'cisco.com': 1.6,
    'mcafee.com': 1.5,
    'kaspersky.com': 1.5,
    'trendmicro.com': 1.5,
    'ibm.com': 1.5,
    'rapid7.com': 1.6,
    'sophos.com': 1.5,
    'tenable.com': 1.6,
    'proofpoint.com': 1.5,
    'okta.com': 1.5,
    'ceccouncil.org': 1.6,
    'symantec.com': 1.5,
    'portswigger.net': 1.7
}

def check_rate_limit():
    global request_timestamps
    current_time = datetime.now()
    # Remove timestamps older than the window
    request_timestamps = [ts for ts in request_timestamps 
                        if current_time - ts < timedelta(seconds=RATE_LIMIT_WINDOW)]
    
    if len(request_timestamps) >= MAX_REQUESTS_PER_WINDOW:
        return False
    
    request_timestamps.append(current_time)
    return True

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def search_with_fallback(query, page=1):
    if not check_rate_limit():
        time.sleep(2)  # Wait if rate limited
        
    results = []
    random.shuffle(SEARCH_ENGINES)  # Randomize search engine order
    
    for engine in SEARCH_ENGINES:
        try:
            headers = get_random_headers()
            params = engine['params'](query, page)
            response = requests.get(
                engine['url'],
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # If we got results, break the loop
            if response.status_code == 200:
                results = parse_search_results(response.text, engine['name'])
                if results:
                    break
                
        except Exception as e:
            print(f"Error with {engine['name']}: {str(e)}")
            continue
            
        time.sleep(random.uniform(1, 3))  # Random delay between requests
    
    # Apply domain prioritization
    for result in results:
        score = 1.0
        parsed_url = urlparse(result['url'])
        domain = parsed_url.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if the domain or any parent domain is trusted
        domain_parts = domain.split('.')
        for i in range(len(domain_parts) - 1):
            check_domain = '.'.join(domain_parts[i:])
            if check_domain in TRUSTED_DOMAINS:
                score *= TRUSTED_DOMAINS[check_domain]
                break
        
        # Add content relevance score
        query_terms = query.lower().split()
        content = (result['title'] + ' ' + result['summary']).lower()
        for term in query_terms:
            if term in content:
                score += 0.2
        
        result['score'] = round(score, 2)
    
    # Sort results by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def parse_search_results(html_content, engine_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    if engine_name == 'Google':
        for div in soup.find_all('div', class_='g'):
            try:
                title_elem = div.find('h3')
                link_elem = div.find('a')
                snippet_elem = div.find('div', class_='VwiC3b')
                
                if title_elem and link_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text,
                        'url': link_elem['href'],
                        'summary': snippet_elem.text,
                        'score': 1.0
                    })
            except Exception:
                continue
                
    elif engine_name == 'Bing':
        for li in soup.find_all('li', class_='b_algo'):
            try:
                title_elem = li.find('h2')
                link_elem = title_elem.find('a') if title_elem else None
                snippet_elem = li.find('div', class_='b_caption')
                
                if title_elem and link_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text,
                        'url': link_elem['href'],
                        'summary': snippet_elem.text,
                        'score': 1.0
                    })
            except Exception:
                continue
                
    elif engine_name == 'DuckDuckGo':
        for result in soup.find_all('div', class_='result'):
            try:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text,
                        'url': title_elem['href'],
                        'summary': snippet_elem.text,
                        'score': 1.0
                    })
            except Exception:
                continue
    
    return results

def get_page_info(url):
    try:
        headers = get_random_headers()
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title = soup.title.string if soup.title else urlparse(url).netloc
        
        # Get description/summary
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        else:
            # If no meta description, get first paragraph or first 200 characters of text
            first_p = soup.find('p')
            if first_p:
                description = first_p.get_text()[:200]
            else:
                description = soup.get_text()[:200]
        
        return {
            'title': title.strip() if title else url,
            'summary': description.strip(),
            'url': url,
            'score': 1.0
        }
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return {
            'title': urlparse(url).netloc,
            'summary': "Unable to fetch page content",
            'url': url,
            'score': 0.5
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})
    
    try:
        # Add cybersecurity context to the query
        cyber_query = f"{query} (cybersecurity OR 'information security' OR 'ethical hacking' OR 'penetration testing')"
        results = search_with_fallback(cyber_query)
        
        # Enhance results with page info and apply scoring
        enhanced_results = []
        for result in results[:10]:  # Limit to top 10 results
            enhanced_result = get_page_info(result['url'])
            enhanced_result['score'] = result['score']  # Preserve the score from search results
            enhanced_results.append(enhanced_result)
            time.sleep(0.2)  # Small delay between requests
        
        # Final sort by score
        enhanced_results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({'results': enhanced_results})
    
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
