# B Corp Company Scraper

**This project was developed as a personal initiative based on a data scraping request on Upwork, for which I was not selected. It serves as a demonstration of my capabilities in web scraping and data processing.**

This Python script is designed to scrape comprehensive data about certified B Corporations from the official B Corporation website (`bcorporation.net`) using their underlying Typesense API. It extracts detailed information about each company, processes it, and saves the results into both JSON and CSV formats.

## Tech Stack

*   **Python**: The core programming language used for the script.
*   **Requests**: For making HTTP requests to the B Corporation API.
*   **Pydantic**: For data validation and serialization, ensuring robust and structured data handling.
*   **JSON**: For handling JSON data, both for API requests and output.
*   **CSV**: For writing the extracted data into CSV format.
*   **`time` module**: For introducing delays to prevent overwhelming the API.
*   **`typing` module**: For type hinting, enhancing code readability and maintainability.
*   **`datetime` module**: For handling and formatting date/time information.

## Features

*   **Automated Data Extraction**: Fetches company data directly from the B Corporation API.
*   **Pagination Handling**: Automatically iterates through all available pages to collect the complete dataset.
*   **Robust Data Model**: Utilizes Pydantic for strict data validation and structured output, ensuring data integrity.
*   **Derived Fields**: Automatically calculates and formats fields like `headquarters`, `certified_since_date`, `website_url`, and `overall_impact_score_float` from raw API responses.
*   **Multiple Output Formats**: Saves the scraped data into two convenient formats:
    *   `b_corp_companies_data.json`: For structured, machine-readable data.
    *   `b_corp_companies_data.csv`: For easy viewing and analysis in spreadsheet software.
*   **Error Handling**: Includes basic error handling for network requests and JSON parsing.

## Installation

To set up and run this scraper, you need Python 3.7+ and the following libraries.

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/NaijaB0T/Scrape-Bcorporation-Businesses
    cd b-corp-scraper
    ```


2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required Python packages:**
    ```bash
    pip install requests pydantic
    ```
    *(Note: `json`, `time`, `csv`, `typing`, `datetime` are typically part of Python's standard library and do not require separate installation.)*

## Usage

Once installed, you can run the scraper from your terminal:

```bash
python scrape.py
```

The script will start fetching data page by page and print its progress to the console.

## Output

Upon successful completion, two files will be generated in the same directory as the script:

*   `b_corp_companies_data.json`: Contains a list of dictionaries, where each dictionary represents a B Corp company with all extracted fields.
*   `b_corp_companies_data.csv`: Contains the same data in a comma-separated values format, suitable for spreadsheet applications.

The data fields included for each company are:

*   `name`: The company's official name.
*   `headquarters`: The company's headquarters location (City, Province, Country).
*   `certified_since_timestamp`: The original timestamp of certification.
*   `certified_since_date`: The derived date of certification in `YYYY-MM-DD` format.
*   `industry`: The industry the company operates in.
*   `sector`: The sector the company belongs to.
*   `operates_in`: A list of countries where the company operates.
*   `website_url`: The derived official website URL on `bcorporation.net`.
*   `description`: A brief description of the company.
*   `overall_impact_score_str`: The overall impact score as a string.
*   `overall_impact_score_float`: The overall impact score as a floating-point number.
*   `company_slug`: The unique slug used in the B Corp website URL.

## License

This project is open-source and available under the [MIT License](LICENSE).
