
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import mysql.connector

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['product_name']
        if product_name:
            flipkart_result = search_flipkart(product_name)
            if flipkart_result:
                check_query = "SELECT * FROM product WHERE name = %s"
                cursor.execute(check_query, (flipkart_result['title'],))
                existing_product = cursor.fetchone()

                if existing_product:
                    stored_price = existing_product[2]
                    try:
                        stored_price_cleaned = ''.join(char for char in stored_price if char.isdigit() or char in {',', '.'})
                        stored_price = float(stored_price_cleaned.replace(',', ''))
                    except ValueError:
                        stored_price = None

                    current_price = flipkart_result['price']
                    price_difference = stored_price - current_price

                    return render_template('result.html',
                                            title=flipkart_result['title'],
                                            current_price=current_price,
                                            stored_price=stored_price,
                                            price_difference=price_difference)

                else:
                    return render_template('result.html',
                                            title=flipkart_result['title'],
                                            current_price=flipkart_result['price'],
                                            stored_price="N/A",
                                            price_difference="N/A")

    return render_template('index.html')

if __name__ == '__main__':
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pass",
        database="db_name"
    )

    cursor = db_connection.cursor()

    app.run(debug=True,port=8000)
    cursor.close()
    db_connection.close()
