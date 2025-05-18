import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
from entry import Entry
import json

class EksiScraper:
    def __init__(self, base_url: str, interrupted_file: Optional[str] = None):
        self.base_url = base_url
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://eksisozluk.com/',
        }        
        self.interrupted_file = interrupted_file

    def get_page_count(self, soup: BeautifulSoup) -> int:
        pager = soup.find('div', class_='pager')
        if not pager or 'data-pagecount' not in pager.attrs:
            print("Could not find pager or page count. Scraping only first page.")
            return 1
        try:
            return int(pager['data-pagecount'])
        except ValueError:
            print("Could not parse page count. Scraping only first page.")
            return 1

    def parse_entry(self, entry_element) -> Optional[Entry]:
        entry_id = entry_element.get('data-id')
        if not entry_id:
            return None
        content_div = entry_element.find('div', class_='content')
        date_div = entry_element.find('a', class_='entry-date')
        content = content_div.get_text(separator='\n', strip=True) if content_div else "N/A"
        author = entry_element.get('data-author', "N/A")
        timestamp_raw = date_div.get_text(strip=True) if date_div else "N/A"
        return Entry(
            id=entry_id,
            author=author,
            timestamp=timestamp_raw,
            content=content,
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def append_to_interrupted(self, entry: Entry):
        if self.interrupted_file:
            try:
                with open(self.interrupted_file, 'a', encoding='utf-8') as f:
                    json.dump(entry.__dict__, f, ensure_ascii=False)
                    f.write('\n')
            except Exception as e:
                print(f"Error writing to interrupted file: {e}")

    def scrape(self) -> List[Entry]:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape job...")
        entries: List[Entry] = []
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            last_page = self.get_page_count(soup)
            print(f"Found {last_page} pages.")
            # Scrape from first page to last page (inclusive)
            for current_page in range(1, last_page + 1):
                page_url = f"{self.base_url}?p={current_page}"
                print(f"Scraping page {current_page}: {page_url}")
                try:
                    response_page = requests.get(page_url, headers=self.headers, timeout=20)
                    response_page.raise_for_status()
                    soup_page = BeautifulSoup(response_page.text, 'html.parser')
                    entry_list = soup_page.find('ul', id='entry-item-list')
                    if not entry_list:
                        print(f"Could not find entry list on page {current_page}.")
                        continue
                    page_entries = entry_list.find_all('li', attrs={'data-id': True})
                    if not page_entries:
                        print(f"No entries with data-id found on page {current_page}.")
                        continue
                    print(f"Found {len(page_entries)} entries on page {current_page}.")
                    for entry_element in page_entries:
                        entry = self.parse_entry(entry_element)
                        if entry:
                            entries.append(entry)
                            self.append_to_interrupted(entry)
                except requests.exceptions.RequestException as e:
                    print(f"HTTP Request error for page {current_page}: {e}")
                    continue
                except Exception as e:
                    print(f"An error occurred processing page {current_page}: {e}")
                    continue
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scrape job finished. {len(entries)} entries scraped.")
        except requests.exceptions.RequestException as e:
            print(f"HTTP Request error during initial page load: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during scraping setup: {e}")
        return entries 