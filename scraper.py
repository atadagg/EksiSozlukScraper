import requests
from bs4 import BeautifulSoup
import time
import schedule
import json
import os
import re # Import regex for timestamp parsing

BASE_URL = "https://eksisozluk.com/6-subat-2023-deprem-yardimlasma-basligi--7568616"
# ID_STORAGE_FILE = "scraped_ids.txt" # Old file
METADATA_FILE = "entry_metadata.json" # New file for {id: timestamp}
DATA_OUTPUT_FILE = "scraped_data.jsonl"
CHECK_EDITS_PAGES = 20 # How many recent pages to check for edits hourly
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# --- Helper Functions ---

def load_metadata():
    """Loads the entry metadata (id: latest_timestamp) from the JSON file."""
    metadata = {}
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {METADATA_FILE} is corrupted or not valid JSON. Starting fresh.")
        except Exception as e:
            print(f"Error loading metadata from {METADATA_FILE}: {e}")
    # Ensure loaded keys are strings if they somehow got saved as ints
    return {str(k): v for k, v in metadata.items()} 

def save_metadata(metadata):
    """Saves the entry metadata (id: latest_timestamp) to the JSON file."""
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4) # Use indent for readability
    except Exception as e:
        print(f"Error saving metadata to {METADATA_FILE}: {e}")

def parse_latest_timestamp(timestamp_str):
    """Extracts the latest timestamp (edit time if available) from the string."""
    if not timestamp_str:
        return None
    # Format is like 'DD.MM.YYYY HH:MM' or 'DD.MM.YYYY HH:MM ~ DD.MM.YYYY HH:MM'
    parts = timestamp_str.split('~')
    latest_part = parts[-1].strip() # Get the part after '~' or the only part
    
    # Basic validation regex (DD.MM.YYYY HH:MM)
    if re.match(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", latest_part):
        return latest_part
    else:
        # print(f"Warning: Could not parse timestamp: {timestamp_str}") # Optional warning
        return timestamp_str # Return original if parsing fails, better than None


def append_data(data, is_update=False):
    """Appends newly scraped data to the output file, optionally marking updates."""
    try:
        with open(DATA_OUTPUT_FILE, 'a', encoding='utf-8') as f:
            if is_update:
                data['update_reason'] = 'edit' # Mark that this is an update due to edit
            else:
                 data.pop('update_reason', None) # Remove field if it existed and is not an update
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error appending data: {e}")


def scrape_eksi():
    """Scrapes the target Ekşi Sözlük pages backward for new entries."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape job...")
    metadata = load_metadata()
    initial_entry_count = len(metadata)
    new_entries_found_total = 0
    
    # Keep track of new ids added in this run to update metadata correctly
    current_run_metadata_updates = {} 

    try:
        # 1. Get the main page to find the last page number
        headers = {'User-Agent': USER_AGENT}
        print(f"Fetching base URL to find page count: {BASE_URL}")
        response = requests.get(BASE_URL, headers=headers, timeout=20)
        response.raise_for_status() # raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # find the pager and get the last page number
        pager = soup.find('div', class_='pager') # pager is the pagination bar
        if not pager or 'data-pagecount' not in pager.attrs:
            print("Could not find pager or page count. Scraping only first page.")
            last_page = 1
        else:
            try:
                last_page = int(pager['data-pagecount'])
                print(f"Found {last_page} pages.")
            except ValueError:
                print("Could not parse page count. Scraping only first page.")
                last_page = 1

        # 2. scrape pages backward from last_page
        for current_page in range(last_page, 0, -1):
            target_url = f"{BASE_URL}?p={current_page}"
            print(f"Scraping page {current_page}: {target_url}")
            stop_scraping_previous_pages = False
            new_entries_on_this_page = 0

            try:
                response_page = requests.get(target_url, headers=headers, timeout=20)
                response_page.raise_for_status()
                soup_page = BeautifulSoup(response_page.text, 'html.parser')

                entry_list = soup_page.find('ul', id='entry-item-list')
                if not entry_list:
                    print(f"Could not find entry list on page {current_page}.")
                    continue # try the previous page

                entries = entry_list.find_all('li', attrs={'data-id': True})
                if not entries:
                    print(f"No entries with data-id found on page {current_page}.")
                    continue # try the previous page

                print(f"Found {len(entries)} entries on page {current_page}.")

                # process entries on the current page
                for entry in entries:
                    entry_id = entry.get('data-id')
                    if not entry_id:
                        continue # skip if no ID

                    if entry_id in metadata:
                        # Found an entry we already scraped, stop going to previous pages
                        print(f"  Found known entry ID {entry_id} on page {current_page}. Stopping backward scrape.")
                        stop_scraping_previous_pages = True
                        break # Stop processing entries on this page
                    else:
                        # New entry found, process it
                        content_div = entry.find('div', class_='content')
                        # author_div = entry.find('a', class_='entry-author') # Use data-author instead
                        date_div = entry.find('a', class_='entry-date')

                        content = content_div.get_text(separator='\\n', strip=True) if content_div else "N/A"
                        author = entry.get('data-author', "N/A") # Use data-author attribute
                        timestamp = date_div.get_text(strip=True) if date_div else "N/A"

                        # Basic cleaning/extraction from timestamp
                        latest_timestamp = parse_latest_timestamp(timestamp)
                        if latest_timestamp is None:
                            print(f"  Warning: Skipping entry {entry_id} due to unparsable timestamp: {timestamp}")
                            continue

                        entry_data = {
                            'id': entry_id,
                            'author': author,
                            'timestamp': latest_timestamp, # Store the parsed latest timestamp
                            'content': content,
                            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        }

                        append_data(entry_data, is_update=False)
                        current_run_metadata_updates[entry_id] = latest_timestamp # Mark for metadata update
                        new_entries_on_this_page += 1
                        # print(f"  New entry added: ID={entry_id}, Author={author}")

                new_entries_found_total += new_entries_on_this_page
                if new_entries_on_this_page > 0:
                     print(f"  Added {new_entries_on_this_page} new entries from page {current_page}.")

                # if we found a known entry, stop the outer loop (pages)
                if stop_scraping_previous_pages:
                    break

            except requests.exceptions.RequestException as e:
                print(f"HTTP Request error for page {current_page}: {e}")
                # optionally decide whether to stop or continue to previous page on error
                break
            except Exception as e:
                 print(f"An error occurred processing page {current_page}: {e}")
                 # optionally decide whether to stop or continue
                 break # stop on other errors for safety

        # 3. Save metadata if new ones were found
        if current_run_metadata_updates:
            print(f"Finished scraping. Added {new_entries_found_total} new entries in total.")
            metadata.update(current_run_metadata_updates) # Add new entries to metadata
            save_metadata(metadata)
        else:
            print("Finished scraping. No new entries found.")

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request error during initial page load: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during scraping setup: {e}")
    finally:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scrape job finished.")


# Scheduling (Delete this section if you don't want to schedule the job inside the script)

print("Setting up schedule...")
# run once immediately
scrape_eksi()

# schedule the job every 10 minutes
schedule.every(10).minutes.do(scrape_eksi)

print("Scheduler started. waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(1) # wait 1 second between checks 