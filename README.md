# Flipkart Product Scraper and Database Interaction

## Overview
This Python script allows users to search for a product on Flipkart, retrieve its information, and interact with a MySQL database for storing and comparing prices.

## Features
1. **Flipkart Search**: Utilizes web scraping with BeautifulSoup and requests to find product information on Flipkart.

2. **Database Interaction**: Connects to a MySQL database and checks whether the product is already stored. Inserts new products if not found.

3. **Scraping Product Information**: Extracts product title and price from the Flipkart search results.

4. **Price Comparison**: Compares the scraped price with the stored price in the database and calculates the price difference.

## Database Configuration
- Host: localhost
- User: root
- Password: 
- Database: Database_name

## Execution
1. Run the script.
2. Enter a product name when prompted.
3. Retrieves and displays Flipkart product information.
4. Compares prices with the stored value in the MySQL database.
5. Inserts new product information into the database if not already present.
6. Outputs relevant information and stores price difference in 'price_difference.txt'.

## Dependencies
- requests
- BeautifulSoup
- mysql.connector

## Usage Notes
- Ensure the MySQL database is set up with the specified configuration before running the script.
- The script runs in an infinite loop, allowing users to input multiple product names until manually stopped.

## Error Handling
- The script provides error handling for database interactions and conversion issues when comparing prices.

Feel free to modify the script to suit your specific needs or integrate it into other projects.
