import requests
from bs4 import BeautifulSoup
import mysql.connector

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


    raw_price = product_price_element.get_text() if product_price_element else "N/A"
    cleaned_price = ''.join(char for char in raw_price if char.isdigit() or char in {',', '.'})

    product_price = float(cleaned_price.replace(',', '')) if cleaned_price else "N/A"

    product_info = {
        'title': product_title.strip(),
        'price': product_price,
    }

    return product_info


db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="engine"
)

cursor = db_connection.cursor()


product_name = input("Enter a product name: ")
if product_name:
    flipkart_result = search_flipkart(product_name)

    if flipkart_result:
        print("\nFlipkart Product Information:")
        print(f"Title: {flipkart_result['title']}")
        print(f"Price: ₹{flipkart_result['price']:.2f}")


        check_query = "SELECT * FROM product WHERE name = %s"
        cursor.execute(check_query, (flipkart_result['title'],))
        existing_product = cursor.fetchone()

        if existing_product:

            stored_price = existing_product[2]

            try:

                stored_price_cleaned = ''.join(char for char in stored_price if char.isdigit() or char in {',', '.'})
                stored_price = float(stored_price_cleaned.replace(',', ''))
            except ValueError:
                print("Error: Unable to convert stored price to float.")
                stored_price = None

            current_price = flipkart_result['price']

            if stored_price is not None:
                print(f"Stored Price in Database: ₹{stored_price:.2f}")
                print(f"Current Price on Flipkart: ₹{current_price:.2f}")


                price_difference = stored_price - current_price
                print(f"Price Difference: ₹{price_difference:.2f}")


                with open("price_difference.txt", "wb") as file:
                    file.write(f"Price Difference for {flipkart_result['title']}: ₹{price_difference:.2f}".encode('utf-8'))
            else:
                print("Error: Unable to compare prices due to conversion issues.")
        else:
            print("Product not found in the database.")
    else:
        print("Product information not available or price is not found.")
else:
    print("No product name entered. Exiting.")


cursor.close()
db_connection.close()
