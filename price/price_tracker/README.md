Flask Product Price Track:
This Flask application allows users to track the prices of products on Flipkart. It utilizes web scraping to gather product information from the Flipkart website and compares it with stored prices in a MySQL database.

Features:
Product Search: Users can enter the name of a product, and the application will retrieve information on the first result from Flipkart.
Price Tracking: The application checks if the product is already stored in the database. If it is, it compares the current price with the stored price, providing users with the price difference.
Database Integration: The application uses MySQL to store product information, including name and price.
Setup
Clone the Repository:
git clone https://github.com/gowtham281/price-tracker.git
cd price-tracker
Install Dependencies:


Configure MySQL Database:

Create a MySQL database named engine.
Update the host, user, password fields in the app.py file with your MySQL credentials.
Run the Application:

python app.py
The application will be accessible at http://localhost:5000/.

Usage
Visit http://localhost:5000/ in your web browser.
Enter the name of the product you want to track and submit the form.
The application will display information about the product, including the current price and any price difference if the product is already in the database.
Notes
This application is designed for educational purposes and may be subject to changes based on Flipkart's website structure.
Feel free to customize this template based on your specific requirements and add any additional information that may be helpful for users and contributors.
