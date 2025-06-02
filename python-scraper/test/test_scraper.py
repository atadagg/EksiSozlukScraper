import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_module import EksiScraper
from entry import Entry

class TestEksiScraper(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://eksisozluk.com/test-topic"
        self.scraper = EksiScraper(self.base_url)

    def test_get_page_count_with_valid_pager(self):
        # Create a mock BeautifulSoup object with a valid pager
        html = '<div class="pager" data-pagecount="5"></div>'
        soup = BeautifulSoup(html, 'html.parser')
        page_count = self.scraper.get_page_count(soup)
        self.assertEqual(page_count, 5)

    def test_get_page_count_without_pager(self):
        # Create a mock BeautifulSoup object without a pager
        html = '<div>No pager here</div>'
        soup = BeautifulSoup(html, 'html.parser')
        page_count = self.scraper.get_page_count(soup)
        self.assertEqual(page_count, 1)

    def test_get_page_count_with_invalid_data(self):
        # Create a mock BeautifulSoup object with invalid page count
        html = '<div class="pager" data-pagecount="invalid"></div>'
        soup = BeautifulSoup(html, 'html.parser')
        page_count = self.scraper.get_page_count(soup)
        self.assertEqual(page_count, 1)

    def test_parse_entry_with_valid_data(self):
        # Create a mock entry element with valid data
        html = '''
        <li data-id="123" data-author="test_user">
            <div class="content">Test content</div>
            <a class="entry-date">20.03.2024 12:00</a>
        </li>
        '''
        entry_element = BeautifulSoup(html, 'html.parser').find('li')
        entry = self.scraper.parse_entry(entry_element)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.id, "123")
        self.assertEqual(entry.author, "test_user")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.timestamp, "20.03.2024 12:00")
        self.assertIsNotNone(entry.scraped_at)

    def test_parse_entry_with_missing_data(self):
        # Create a mock entry element with missing data
        html = '<li data-id="123"></li>'
        entry_element = BeautifulSoup(html, 'html.parser').find('li')
        entry = self.scraper.parse_entry(entry_element)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.id, "123")
        self.assertEqual(entry.author, "N/A")
        self.assertEqual(entry.content, "N/A")
        self.assertEqual(entry.timestamp, "N/A")
        self.assertIsNotNone(entry.scraped_at)

    def test_parse_entry_without_id(self):
        # Create a mock entry element without an ID
        html = '<li>No ID here</li>'
        entry_element = BeautifulSoup(html, 'html.parser').find('li')
        entry = self.scraper.parse_entry(entry_element)
        self.assertIsNone(entry)

    @patch('builtins.open', new_callable=MagicMock)
    def test_append_to_interrupted(self, mock_open):
        # Test appending to interrupted file
        scraper = EksiScraper(self.base_url, interrupted_file="test.jsonl")
        entry = Entry(
            id="123",
            author="test_user",
            timestamp="20.03.2024 12:00",
            content="Test content",
            scraped_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.scraper.append_to_interrupted(entry)
        mock_open.assert_called_once()

    @patch('requests.get')
    def test_scrape_successful(self, mock_get):
        # Mock successful response with multiple pages
        mock_response = MagicMock()
        mock_response.text = '''
        <div class="pager" data-pagecount="2"></div>
        <ul id="entry-item-list">
            <li data-id="1" data-author="user1">
                <div class="content">Content 1</div>
                <a class="entry-date">20.03.2024 12:00</a>
            </li>
        </ul>
        '''
        mock_get.return_value = mock_response

        entries = self.scraper.scrape()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, "1")
        self.assertEqual(entries[0].author, "user1")
        self.assertEqual(entries[0].content, "Content 1")

    @patch('requests.get')
    def test_scrape_with_request_error(self, mock_get):
        # Mock request error
        mock_get.side_effect = Exception("Connection error")
        entries = self.scraper.scrape()
        self.assertEqual(len(entries), 0)

    @patch('requests.get')
    def test_scrape_with_invalid_html(self, mock_get):
        # Mock response with invalid HTML
        mock_response = MagicMock()
        mock_response.text = '<div>Invalid HTML</div>'
        mock_get.return_value = mock_response

        entries = self.scraper.scrape()
        self.assertEqual(len(entries), 0)

if __name__ == '__main__':
    unittest.main() 