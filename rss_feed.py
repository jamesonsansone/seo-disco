import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the environment variables from .env

# Now you can access the environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Assuming OpenAI API key is set in your environment variables or securely stored
# openai.api_key = 'your_openai_api_key_here'

# Function 1: Generate Filtered Articles List
def fetch_filtered_articles(feed_url):
    response = requests.get(feed_url)
    rss_data = response.content
    root = ET.fromstring(rss_data)
    data = []
    for item in root.findall('.//item'):
        link = item.find('link').text
        title = item.find('title').text
        pubDate = item.find('pubDate').text
        categories = ', '.join([category.text for category in item.findall('category')])
        description = ET.tostring(item.find('description'), method='text', encoding='utf-8').decode().strip()
        data.append({"Link": link, "Title": title, "Publication Date": pubDate, "Categories": categories, "Description": description})
    df = pd.DataFrame(data)
    return df[df['Categories'].apply(lambda x: '401(k)' in x or '403(b)' in x or 'benefits' in x or 'benefit' in x)]

# Function 2: Write Social Media Post
def generate_social_media_post(article, role, tone_of_voice):
    client = OpenAI()
    prompt = f"You are a {role} tasked with creating content for social media. Considering a tone that is {tone_of_voice}, generate a LinkedIn post for the following article:\n\n{article['Title']}\n{article['Description']}"
    response = client.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    return response.choices[0].text

# Streamlit App
def main():
    st.title("Social Media Post Generator for HR Articles")

    feed_url = "https://www.planadviser.com/news/compliance/feed/"
    articles_df = fetch_filtered_articles(feed_url)
    
    article_titles = articles_df['Title'].tolist()
    selected_title = st.selectbox("Select an Article", options=article_titles)
    
    selected_article = articles_df.loc[articles_df['Title'] == selected_title].iloc[0]
    
    role = st.text_input("Role", value="HR professional")
    tone_of_voice = st.text_input("Tone of Voice", value="informative and engaging")
    
    if st.button("Generate Post"):
        post_content = generate_social_media_post(selected_article, role, tone_of_voice)
        st.text_area("Generated Post", value=post_content, height=150)

if __name__ == "__main__":
    main()
