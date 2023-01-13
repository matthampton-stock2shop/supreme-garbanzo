from flask import Flask, request, abort
import os
import products_db

app = Flask(__name__)

@app.errorhandler(products_db.ValidationError)
def handle_validation_error(e):
    return {"ok": False}, 400

@app.post("/products")
def post_products():
    products = request.json
    products_db.set_products(products)
    return {"ok": True}

@app.get("/products")
def get_products():
    return products_db.get_products()

@app.post("/products/<string:sku>")
def post_product(sku):
    product = request.json
    product['sku'] = sku
    products_db.upsert_product(product)
    return {"ok": True}

@app.get("/products/<string:sku>")
def get_product(sku):
    product = products_db.get_product(sku)
    if not product:
        abort(404)
    return product


if __name__ == '__main__':
    products_db.init(os.path.join(os.path.dirname(__file__), "data", "db.sqlite"))
    app.run()