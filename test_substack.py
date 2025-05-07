import requests
from bs4 import BeautifulSoup

# Test Substack search page
url = "https://substack.com/publications?q=marketing"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try different CSS selectors to find publications
    selectors_to_try = [
        '.publication-card', 
        '.substackCard', 
        '.stack-list-item',
        'a[href*="substack.com"]',
        '.publication',
        '.stack'
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        print(f"Selector '{selector}': found {len(elements)} elements")
        
        # Print the first element to see structure
        if elements:
            print(f"First element structure: {elements[0]}")
            
    # Try to extract links directly
    links = [a['href'] for a in soup.find_all('a', href=True) 
             if 'substack.com' in a['href'] and not a['href'].startswith('https://substack.com/publications')]
    print(f"Found {len(links)} links to Substack newsletters")
    if links:
        print(f"Example links: {links[:3]}")
        
    # Save the HTML for inspection
    with open("substack_search.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved HTML to substack_search.html for inspection")
else:
    print(f"Failed to access Substack: {response.status_code}")