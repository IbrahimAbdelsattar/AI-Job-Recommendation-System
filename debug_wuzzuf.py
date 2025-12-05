import requests
from bs4 import BeautifulSoup

def debug_wuzzuf():
    print("Debugging Wuzzuf HTML...")
    url = "https://wuzzuf.net/search/jobs/?q=Software+Engineer&a=hpb"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Print all h2 classes
        print("\n--- H2 Tags ---")
        for h2 in soup.find_all('h2')[:5]:
            print(f"H2: {h2.get_text(strip=True)}")
            print(f"Classes: {h2.get('class')}")
            parent = h2.find_parent('div')
            if parent:
                print(f"Parent Div Classes: {parent.get('class')}")
        
        # Print all a tags inside h2
        print("\n--- Links in H2 ---")
        for h2 in soup.find_all('h2')[:5]:
            a = h2.find('a')
            if a:
                print(f"Link: {a['href']}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_wuzzuf()
