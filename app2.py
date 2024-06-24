from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
TEST_SERVER_URL = "http://20.244.56.144/test/companies/{company}/categories/{category}/products"
COMPANIES = ["AMZ", "FLE", "SHB", "NAO", "AZO"]
CATEGORIES = ["Phone", "Computer", "Pendrive", "Remote", "Speaker", "Mouse", "Keypad", "Bluetooth"]

def fetch_products(company, category, top, min_price, max_price):
    url = TEST_SERVER_URL.format(company=company, category=category)
    params = {"top": top, "minPrice": min_price, "maxPrice": max_price}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

@app.route('/categories/<category>/products', methods=['GET'])
def get_top_products(category):
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    top = int(request.args.get('top', 10))
    min_price = request.args.get('minPrice', 0)
    max_price = request.args.get('maxPrice', float('inf'))
    sort_by = request.args.get('sortBy')
    order = request.args.get('order', 'asc')

    products = []
    for company in COMPANIES:
        company_products = fetch_products(company, category, top, min_price, max_price)
        products.extend(company_products)

    if sort_by:
        products.sort(key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))

    paginated_products = products[:top]
    for idx, product in enumerate(paginated_products, start=1):
        product["id"] = idx

    return jsonify(paginated_products)

@app.route('/categories/<category>/products/<int:product_id>', methods=['GET'])
def get_product_details(category, product_id):
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    for company in COMPANIES:
        products = fetch_products(company, category, 10, 0, float('inf'))
        for product in products:
            if product.get("id") == product_id:
                return jsonify(product)
    
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(port=9877)
