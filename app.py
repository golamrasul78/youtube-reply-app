import streamlit as st
from googleapiclient.discovery import build
import requests

# API Keys from secrets
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
st.set_page_config(page_title="YouTube Auto‑Reply Generator", layout="wide")
st.title("YouTube Comment Auto‑Replier (Free + Gemini)")

def get_comments(video_id, max_comments=10):
    comments = []
    try:
        resp = youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=max_comments, textFormat="plainText"
        ).execute()
        for item in resp.get("items", []):
            snip = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({"author": snip["authorDisplayName"], "text": snip["textDisplay"]})
    except Exception as e:
        st.error(f"Comment fetch error: {e}")
    return comments

def generate_free_reply(comment):
    txt = comment.lower()
    if "source" in txt:
        return "Thanks for asking! We'll share detailed sources soon."
    elif "bs" in txt:
        return "We understand your concern—let’s keep things respectful and constructive."
    elif "diverse" in txt:
        return "Diversity matters a lot! We aim to include all perspectives fairly."
    else:
        return "Thank you for your thoughts! We appreciate your engagement."

def generate_gemini_reply(comment):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Reply politely and constructively to this YouTube comment:\n'{comment}'"}]}]
    }
    try:
        res = requests.post(endpoint, headers=headers, json=payload)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Gemini error: {e}"

video_id = st.text_input("Enter YouTube Video ID")
if st.button("Fetch Comments"):
    if not video_id.strip():
        st.warning("Please enter a valid video ID.")
    else:
        comments = get_comments(video_id)
        if comments:
            st.write(f"Found {len(comments)} comments:")
            for idx, c in enumerate(comments):
                st.markdown(f"**{c['author']}**: {c['text']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Free Reply", key=f"free_{idx}"):
                        st.success(generate_free_reply(c['text']))
                with col2:
                    if st.button("Gemini Reply", key=f"gemini_{idx}"):
                        st.info(generate_gemini_reply(c['text']))
        else:
            st.warning("No comments found.")