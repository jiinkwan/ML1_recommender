import streamlit as st
import pandas as pd
import numpy as np

def load_data():
    """Load the static dataset."""
    file_path = "output_w_prod_cluster.csv"  # Static file
    return pd.read_csv(file_path)

def get_top_items_by_season(df, top_n=3):
    """Get the most popular items per season, excluding the purchased item later."""
    return df.groupby("Season")["Item Purchased"].apply(lambda x: x.value_counts().index[:top_n]).to_dict()

def get_top_colors_by_season(df, top_n=3):
    """Get the most common colors per season."""
    return df.groupby("Season")["Color"].apply(lambda x: x.value_counts().index[:top_n]).to_dict()

def recommend_items_with_colors(season, purchased_item, purchased_color, top_items, top_colors, item_images):
    """Recommend the top three most popular items for the season (excluding purchased) with color preferences and images."""
    season_items = top_items.get(season, [])
    season_items = [item for item in season_items if item != purchased_item]
    recommended_items = season_items[:3] if len(season_items) >= 3 else season_items
    
    season_colors = top_colors.get(season, [])
    recommended_colors = season_colors[:3] if len(season_colors) >= 3 else season_colors
    
    recommendations = []
    for item, color in zip(recommended_items, recommended_colors):
        image_url = item_images.get((item, color), None)  # Get image URL if available
        recommendations.append((item, color, image_url))
    
    return recommendations if recommendations else [("No recommendation", "No color", None)]

# Load item and color image dataset
image_data_path = "item_color_combinations.csv"  # Ensure correct file path
image_df = pd.read_csv(image_data_path)

# Convert to dictionary for quick lookup
item_images = {(row["Item"], row["Color"]): row["URL"] for _, row in image_df.iterrows()}

# Streamlit UI
st.set_page_config(page_title="Product Recommender", layout="wide")
st.title("🛍️ Product Recommendation System")

# Load data
st.sidebar.header("Dataset Information")
df = load_data()

top_items_by_season = get_top_items_by_season(df)  # Ensure it's defined globally
top_colors_by_season = get_top_colors_by_season(df)

if df is not None:
    st.sidebar.success("Dataset Loaded Successfully!")
    
    # User input for Customer ID
    customer_id = st.sidebar.text_input("Enter Customer ID:")
    
    if customer_id:
        # Check if Customer ID exists
        if customer_id in df.index.astype(str):
            customer_row = df.loc[df.index.astype(str) == customer_id].iloc[0]
            
            st.subheader(f"Customer {customer_id}'s Purchase Information")
            st.write(f"**Item Purchased:** {customer_row['Item Purchased']}")
            st.write(f"**Color:** {customer_row['Color']}")
            st.write(f"**Season:** {customer_row['Season']}")
            
            # Generate recommendations for the customer
            recommendations = recommend_items_with_colors(
                customer_row["Season"], customer_row["Item Purchased"], customer_row["Color"],
                top_items_by_season, top_colors_by_season, item_images
            )
            
            st.subheader("📌 Recommended Products")
            cols = st.columns(3)  # Create three columns for images
            
            for i, (item, color, image_url) in enumerate(recommendations):
                with cols[i % 3]:  # Assign each recommendation to a separate column
                    st.write(f"**{item} in {color}**")
                    if image_url and pd.notna(image_url):
                        st.image(image_url, caption=f"{item} in {color}", use_column_width=True)
                    else:
                        st.write("Image not available")
            
        else:
            st.error("Customer ID not found in the dataset.")
    
    st.success("✅ Ready to generate recommendations!")
