import unittest
import os
import json
from data_manager import DataManager
from entry import Entry
from datetime import datetime

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.test_output_file = "test_output.jsonl"
        self.test_diff_file = "test_diff.jsonl"
        self.data_manager = DataManager(self.test_output_file, self.test_diff_file)
        
        # Create test entries
        self.entry1 = Entry(
            id="1",
            author="test_user",
            timestamp="2024-03-20 12:00:00",
            content="First entry. Second sentence.",
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.entry2 = Entry(
            id="2",
            author="test_user",
            timestamp="2024-03-20 12:01:00",
            content="Second entry. Another sentence.",
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)
        if os.path.exists(self.test_diff_file):
            os.remove(self.test_diff_file)

    def test_save_and_load_data(self):
        # Test saving data
        self.data_manager.save_data([self.entry1, self.entry2])
        self.assertTrue(os.path.exists(self.test_output_file))
        
        # Test loading data
        loaded_data = self.data_manager.load_data()
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0].id, self.entry1.id)
        self.assertEqual(loaded_data[1].id, self.entry2.id)

    def test_diff_new_entry(self):
        # Test diff with new entry
        old_data = [self.entry1]
        new_data = [self.entry1, self.entry2]
        
        diffs = self.data_manager.diff(old_data, new_data)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]['type'], 'new')
        self.assertEqual(diffs[0]['id'], self.entry2.id)

    def test_diff_edited_entry(self):
        # Create modified version of entry1
        modified_entry = Entry(
            id=self.entry1.id,
            author=self.entry1.author,
            timestamp="2024-03-20 12:02:00",
            content="First entry. Second sentence. New content.",
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Test diff with edited entry
        old_data = [self.entry1]
        new_data = [modified_entry]
        
        diffs = self.data_manager.diff(old_data, new_data)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]['type'], 'appended')
        self.assertEqual(diffs[0]['id'], self.entry1.id)
        self.assertEqual(diffs[0]['content'], " New content.")

    def test_diff_completely_edited_entry(self):
        # Create completely modified version of entry1
        modified_entry = Entry(
            id=self.entry1.id,
            author=self.entry1.author,
            timestamp="2024-03-20 12:02:00",
            content="Completely different content.",
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Test diff with completely edited entry
        old_data = [self.entry1]
        new_data = [modified_entry]
        
        diffs = self.data_manager.diff(old_data, new_data)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]['type'], 'edited')
        self.assertEqual(diffs[0]['id'], self.entry1.id)
        self.assertEqual(diffs[0]['content'], "Completely different content.")

    def test_save_diff(self):
        # Create some diffs
        diffs = [
            {'id': '1', 'type': 'new', 'content': 'New content', 'timestamp': '2024-03-20 12:00:00'},
            {'id': '2', 'type': 'edited', 'content': 'Edited content', 'timestamp': '2024-03-20 12:01:00'}
        ]
        
        # Test saving diffs
        self.data_manager.save_diff(diffs)
        self.assertTrue(os.path.exists(self.test_diff_file))
        
        # Verify saved content
        with open(self.test_diff_file, 'r', encoding='utf-8') as f:
            saved_diffs = [json.loads(line) for line in f]
            self.assertEqual(len(saved_diffs), 2)
            self.assertEqual(saved_diffs[0]['type'], 'new')
            self.assertEqual(saved_diffs[1]['type'], 'edited')

if __name__ == '__main__':
    unittest.main() 