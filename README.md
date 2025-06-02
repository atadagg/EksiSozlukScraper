# EksiSozluk Scraper

This project is designed to scrape data from Ekşi Sözlük, process it, and potentially perform some Natural Language Processing (NLP) tasks. It's divided into two main components: a Python-based scraper and a Java-based NLP processor.

## Project Structure

The project is organized into the following main directories:

*   **`python-scraper/`**: This directory contains the Python scripts responsible for scraping data from Ekşi Sözlük. The main entry point for the scraping process is likely `main.py` within this directory.
*   **`java-nlp/`**: This directory houses the Java code used for Natural Language Processing tasks on the scraped data. It appears to use Maven for dependency management and building. The `FileSplitter.java` is a key component here.
*   **`samples/`**: This directory likely contains sample data or example outputs from the scraping or NLP processes.
*   **`venv/`**: This is a Python virtual environment directory, used to manage project-specific dependencies for the Python scraper.

## How to Run

1.  **Python Scraper**: Navigate to the `python-scraper` directory and run `main.py`.
    ```bash
    cd python-scraper
    python main.py 
    ```
    *(Ensure you have the necessary Python dependencies installed, potentially managed by the `venv`)*

2.  **Java NLP Processor**: Navigate to the `java-nlp` directory. You can run `FileSplitter.java` using Maven or an IDE like IntelliJ IDEA.
    *   **Using Maven (example command, might need adjustment):**
        ```bash
        cd java-nlp
        mvn exec:java -Dexec.mainClass="your.package.FileSplitter" 
        ```
        *(Replace `"your.package.FileSplitter"` with the actual package and class name if different)*

## TODO

*   Scraping doesn't work on Linux/servers/Docker (HTTP 403 Error).
*   Investigate and confirm fix for `scraped_data.jsonl` getting zeroed out on connection errors.
*   Turkish NLP task: "Bütün ilk harfleri ünlü yap, doğru olanları listeye koyup hepsini değiştir(? iyi çalışmayabilir)" - *This needs further clarification or refinement.*

## Contributing

Details on how to contribute to the project will be added here.

## License

This project is licensed under the [LICENSE_NAME] - see the `LICENSE` file for details. *(Update `LICENSE_NAME` if applicable)*