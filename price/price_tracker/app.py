from flask import Flask, render_template, request, flash, redirect, url_for
import requests
from bs4 import BeautifulSoup
import mysql.connector
import random
import time
import urllib.parse
import os
import logging

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Securely store your secret key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    # Add more user agents as needed
]

PROXIES = [
    # "http://user:password@proxy1.example.com:8080",
    # "http://user:password@proxy2.example.com:8080",
    # Add proxies if needed
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

def get_proxies():
    if PROXIES:
        proxy = random.choice(PROXIES)
        return {
            "http": proxy,
            "https": proxy,
        }
    else:
        return None

def search_flipkart(product_name):
    base_url = "https://www.flipkart.com"
    encoded_product_name = urllib.parse.quote_plus(product_name)
    search_url = f"{base_url}/search?q={encoded_product_name}"
    logging.info(f"Encoded Search URL: {search_url}")

    try:
        response = requests.get(
            search_url,
            headers=get_headers(),
            proxies=get_proxies(),
            timeout=10
        )
        response.raise_for_status()
        logging.info("Search request successful")  # Logging statement
        time.sleep(random.uniform(3, 5))  # Longer delay between requests
    except requests.RequestException as e:
        logging.error(f"Error fetching search results: {e}")
        return None

    # Optionally, limit the size of the logged HTML to prevent clutter
    # logging.debug(f"HTML Response: {response.text[:500]}")  # Debugging statement

    # Try more general selector for product links
    soup = BeautifulSoup(response.text, 'html.parser')
    product_links = soup.find_all('a', href=True)

    # Filter product links based on known patterns in Flipkart URLs
    product_links = [link for link in product_links if '/p/' in link['href']]

    logging.info(f"Number of products found: {len(product_links)}")  # Logging statement

    if product_links:
        first_product_url = base_url + product_links[0]['href']
        logging.info(f"First product URL: {first_product_url}")  # Logging statement
        product_info_flipkart = scrape_product_info_flipkart(first_product_url)
        return product_info_flipkart
    else:
        logging.warning("No product links found")  # Logging statement
        return None

def scrape_product_info_flipkart(product_url):
    logging.info(f"Scraping product info from: {product_url}")  # Logging statement
    try:
        response = requests.get(
            product_url,
            headers=get_headers(),
            proxies=get_proxies(),
            timeout=10
        )
        response.raise_for_status()
        logging.info("Product info request successful")  # Logging statement
        time.sleep(random.uniform(1, 3))
    except requests.RequestException as e:
        logging.error(f"Error fetching product info: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    # Update selectors based on Flipkart's current HTML structure
    product_title_element = soup.find('span', {'class': 'VU-ZEz'})
    product_price_element = soup.find('div', {'class': 'Nx9bqj CxhGGd'})

    product_title = product_title_element.get_text() if product_title_element else "N/A"
    raw_price = product_price_element.get_text() if product_price_element else "N/A"
    cleaned_price = ''.join(filter(str.isdigit, raw_price))
    product_price = float(cleaned_price) if cleaned_price else "N/A"

    logging.info(f"Product Title: {product_title}")  # Logging statement
    logging.info(f"Product Price: {product_price}")  # Logging statement

    return {
        'title': product_title.strip(),
        'price': product_price,
    }

def initialize_database():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS product (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        price DECIMAL(10, 2) NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute(create_table_query)
        db_connection.commit()
        cursor.close()
        logging.info("Ensured that the 'product' table exists.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating table: {err}")
        exit(1)

@app.route('/', methods=['GET', 'POST'])
def index():
    product_name = ''

    if request.method == 'POST':
        product_name = request.form['product_name'].strip()
        if product_name:
            try:
                # First, scrape Flipkart to get product info
                flipkart_result = search_flipkart(product_name)
                if flipkart_result:
                    scraped_title = flipkart_result['title']
                    current_price = flipkart_result['price']

                    # Check if the scraped_title exists in the database
                    cursor = db_connection.cursor(dictionary=True)
                    check_query = "SELECT * FROM product WHERE name = %s"
                    cursor.execute(check_query, (scraped_title,))
                    existing_product = cursor.fetchone()
                    cursor.close()

                    if existing_product:
                        # Product exists in the database; fetch stored price
                        stored_price = float(existing_product.get('price'))
                        logging.info(f"Product '{scraped_title}' found in database with price: {stored_price}")

                        if isinstance(current_price, (int, float)) and isinstance(stored_price, (int, float)):
                            price_difference = current_price - stored_price
                        else:
                            price_difference = "N/A"

                        logging.info(f"Current Price: {current_price}, Stored Price: {stored_price}, Difference: {price_difference}")

                        return render_template('result.html',
                                               title=scraped_title,
                                               current_price=current_price,
                                               stored_price=stored_price,
                                               price_difference=price_difference)
                    else:
                        # Product does not exist; insert into database
                        insert_cursor = db_connection.cursor()
                        insert_query = "INSERT INTO product (name, price) VALUES (%s, %s)"
                        insert_cursor.execute(insert_query, (scraped_title, current_price))
                        db_connection.commit()
                        insert_cursor.close()

                        return render_template('result.html',
                                               title=scraped_title,
                                               current_price=current_price,
                                               stored_price="N/A",
                                               price_difference="N/A")
                else:
                    flash("Product not found or unable to fetch data. Please try again.")
                    return redirect(url_for('index'))
            except mysql.connector.Error as db_err:
                if db_err.errno == 1062:
                    # Duplicate entry, likely due to race condition or unexpected duplicate
                    logging.error(f"Database error: {db_err}")
                    flash("Product already exists in the database.")
                else:
                    logging.error(f"Database error: {db_err}")
                    flash("An internal error occurred. Please try again later.")
                return redirect(url_for('index'))
        else:
            flash("Please enter a product name.")
            return redirect(url_for('index'))

    return render_template('index.html', product_name=product_name)

if __name__ == '__main__':
    try:
        db_connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),  # Set in environment variables
            database=os.getenv("DB_NAME", "engine")
        )
        logging.info("Database connection successful")
        initialize_database()  # Ensure the 'product' table exists
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to the database: {err}")
        exit(1)

    app.run(debug=True, port=8000)
