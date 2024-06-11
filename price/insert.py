import requests
from bs4 import BeautifulSoup
import mysql.connector

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="engine"
)

cursor = db_connection.cursor()

def search_flipkart(product_name):
    base_url = "https://www.flipkart.com"
    search_url = f"{base_url}/search?q={product_name}"

    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_links = soup.find_all('a', {'class': '_1fQZEK'})

    if product_links:
        first_product_url = base_url + product_links[0]['href']
        product_info_flipkart = scrape_product_info_flipkart(first_product_url)
        return product_info_flipkart
    else:
        return None

def scrape_product_info_flipkart(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_title_element = soup.find('span', {'class': 'B_NuCI'})
    product_price_element = soup.find('div', {'class': '_30jeq3 _16Jk6d'})

    product_title = product_title_element.get_text() if product_title_element else "N/A"
    product_price = product_price_element.get_text() if product_price_element else "N/A"

    product_info = {
        'title': product_title.strip(),
        'price': product_price.strip(),
    }

    return product_info

while True:
    product_name = input("Enter a product name: ")
    flipkart_result = search_flipkart(product_name)

    if flipkart_result and flipkart_result['price'] != "N/A":
        print("\nFlipkart Product Information:")
        print(flipkart_result)

        # Check if the product already exists in the database
        check_query = "SELECT * FROM product WHERE name = %s"
        cursor.execute(check_query, (flipkart_result['title'],))
        existing_product = cursor.fetchone()

        if not existing_product:
            try:
                insert_query = "INSERT INTO product (name, price) VALUES (%s, %s)"
                product_data = (flipkart_result['title'], flipkart_result['price'])
                cursor.execute(insert_query, product_data)

                db_connection.commit()

                print("Product information stored in  database.")
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                print("Failed to insert data into the database.")
        else:
            print("Product already exists in the database. Skipping insertion.")
    else:
        print("Product information not available or price is not found.")
