import requests
import os
import streamlit as st
import pandas as pd
from storage import get_all_products, add_product, update_product, delete_product, get_all_prices, clear_prices
from scraper import scrape_all_products

st.set_page_config(page_title="Amazon Price Tracker", layout="centered")
st.title("Amazon Price Tracker")

tab1, tab2 = st.tabs(["📈 Price History", "🛒 Manage Products"])

with tab1:
    st.subheader("Database: Price History")
    prices = get_all_prices()
    if prices:
        df_prices = pd.DataFrame([{
            "Date": p.date,
            "Title": p.title,
            "URL": p.url,
            "Price": p.price
        } for p in prices])
        # Show latest prices by product
        products = df_prices["Title"].unique()
        selected_product = st.selectbox("Select a product:", products)
        df_selected = df_prices[df_prices["Title"] == selected_product].sort_values("Date")
        st.line_chart(df_selected.set_index("Date")["Price"])
        st.dataframe(df_selected[["Date", "Price"]].sort_values("Date", ascending=False), use_container_width=True)
    else:
        st.info("No price data available. Scrape at least one product.")

with tab2:
    st.subheader("Manage Products")
    # Add Product Form
    with st.form("add_product_form", clear_on_submit=True):
        new_url = st.text_input("Amazon Product URL", "")
        new_title = st.text_input("Product title (optional)", "")
        new_threshold = st.number_input("Alert threshold (optional)", min_value=0.0, step=0.01, format="%.2f")
        submit_add = st.form_submit_button("Add Product")
    if submit_add and new_url:
        add_product(new_url, new_title, new_threshold if new_threshold > 0 else None)
        st.success("Product added!")

    # List all products
    products = get_all_products()
    df_products = pd.DataFrame([{
        "ID": p.id,
        "URL": p.url,
        "Title": p.title,
        "Threshold": p.threshold
    } for p in products])

    if not df_products.empty:
        st.subheader("Tracked products")
        st.dataframe(df_products, use_container_width=True)

        # Edit & Delete
        selected = st.selectbox("Select a product to edit/delete", options=df_products["ID"].tolist())
        selected_product = next((p for p in products if p.id == selected), None)

        if selected_product:
            with st.form("edit_product_form"):
                edit_url = st.text_input("URL", value=selected_product.url)
                edit_title = st.text_input("Title", value=selected_product.title)
                edit_threshold = st.number_input("Threshold", value=selected_product.threshold or 0, min_value=0.0, step=0.01, format="%.2f")
                submit_update = st.form_submit_button("Update")
                submit_delete = st.form_submit_button("Delete")

                if submit_update:
                    update_product(selected_product.id, edit_url, edit_title, edit_threshold)
                    st.success("Product updated!")
                    st.rerun()
                elif submit_delete:
                    delete_product(selected_product.id)
                    st.warning("Product deleted!")
                    st.rerun()
    else:
        st.info("No products tracked yet. Add one above!")

    # Scrape all button
    st.divider()
    if st.button("Scrape all products now"):
        with st.spinner("Scraping in progress..."):
            resp = requests.post(f"{os.getenv('API_URL')}/scrape")
        st.success("Scraping completed!")
        for r in resp.json().get("results", []):
            st.write(f"Product: {r['title']} | Price: {r['price']} | Status: {r['status']}")
    
    st.divider()
    if st.button("Clear all price history", type="primary"):
        clear_prices()
        st.success("All price history has been deleted!")
        st.rerun()  # To refresh the view immediately
