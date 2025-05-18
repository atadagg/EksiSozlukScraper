import os
import json
from typing import List
from entry import Entry
from dataclasses import asdict

class DataManager:
    def __init__(self, data_output_file: str, data_diff_file: str):
        self.data_output_file = data_output_file
        self.data_diff_file = data_diff_file

    def load_data(self) -> List[Entry]:
        data = []
        if os.path.exists(self.data_output_file):
            try:
                with open(self.data_output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        obj = json.loads(line)
                        data.append(Entry(**obj))
            except Exception as e:
                print(f"Error loading data from {self.data_output_file}: {e}")
        return data

    def save_data(self, entries: List[Entry]) -> None:
        try:
            with open(self.data_output_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    json.dump(asdict(entry), f, ensure_ascii=False)
                    f.write('\n')
        except Exception as e:
            print(f"Error saving data to {self.data_output_file}: {e}")

    def diff(self, old_data: List[Entry], new_data: List[Entry]) -> List[dict]:
        old_map = {entry.id: entry for entry in old_data}
        diffs = []
        for entry in new_data:
            old_entry = old_map.get(entry.id) # this is checking if the entry is already in the old data
            if not old_entry: # if the entry is not in the old data, it is a new entry
                diffs.append({'id': entry.id, 'type': 'new', 'content': entry.content, 'timestamp': entry.timestamp})
            elif entry.content != old_entry.content: # if the entry is in the old data, but the content is different, it is an edited entry
                if entry.content.startswith(old_entry.content): # we ignore the edits for the original body(only append the edits after the original body)
                    appended = entry.content[len(old_entry.content):]
                    if appended.strip():
                        diffs.append({'id': entry.id, 'type': 'appended', 'content': appended, 'timestamp': entry.timestamp})
                else:
                    diffs.append({'id': entry.id, 'type': 'edited', 'content': entry.content, 'timestamp': entry.timestamp})
        return diffs

    def save_diff(self, diff: List[dict]) -> None:
        try:
            with open(self.data_diff_file, 'w', encoding='utf-8') as f:
                for entry in diff:
                    json.dump(entry, f, ensure_ascii=False)
                    f.write('\n')
        except Exception as e:
            print(f"Error saving diff to {self.data_diff_file}: {e}")