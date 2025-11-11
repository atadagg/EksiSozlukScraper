import os
import schedule
import time
import json
from dataclasses import asdict
from datetime import datetime
from data_manager import DataManager
from scraper_module import EksiScraper

def save_debug_files(new_data, diff):
    debug_dir = "data_debug"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_data_path = os.path.join(debug_dir, f"new_data_{timestamp}.jsonl")
    diff_path = os.path.join(debug_dir, f"diff_{timestamp}.jsonl")

    # Save new_data
    with open(new_data_path, "w", encoding="utf-8") as f:
        for entry in new_data:
            json.dump(asdict(entry), f, ensure_ascii=False)
            f.write("\n")

    # Save diff
    with open(diff_path, "w", encoding="utf-8") as f:
        for entry in diff:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

def main():
    BASE_URL = "https://eksisozluk.com/6-subat-2023-kahramanmaras-depremi--7568601"
    DATA_OUTPUT_FILE = "scraped_data.jsonl"
    DATA_DIFF_FILE = "data_diff.jsonl"
    INTERRUPTED_FILE = "x_interrupted.jsonl"
    
    data_manager = DataManager(DATA_OUTPUT_FILE, DATA_DIFF_FILE)
    scraper = EksiScraper(BASE_URL, interrupted_file=INTERRUPTED_FILE)
    
    try:
        old_data = data_manager.load_data()
        new_data = scraper.scrape()
        
        # Only proceed if we got some data back
        if new_data:
            diff = data_manager.diff(old_data, new_data)
            print(f"Diff (new entries): {len(diff)}")
            data_manager.save_data(new_data)  # replace old with new
            data_manager.save_diff(diff) # update diff file to pass for processing
            
            # FOR DEBUGGING
            save_debug_files(new_data, diff)

            # Delete interrupted file if it exists (successful scrape)
            if os.path.exists(INTERRUPTED_FILE):
                os.remove(INTERRUPTED_FILE)
                print(f"Deleted {INTERRUPTED_FILE} after successful scrape.")
        else:
            print("No data was scraped, skipping file updates.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Skipping file updates due to error.")
        return

if __name__ == "__main__":
    main()
    schedule.every(10).minutes.do(main)
    print("Scheduler started. Running every 10 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(1)