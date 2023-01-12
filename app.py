from flask import Flask, request
import os
import db

app = Flask(__name__)

@app.post("/products")
def post_products():
    products = request.json
    db.set_products(products)
    return products

@app.get("/products")
def get_products():
    products = request.json
    db.get_products(products)
    return products

if __name__ == '__main__':
    db.init(os.path.join(os.path.dirname(__file__), "data", "db.sqlite"))
    app.run()