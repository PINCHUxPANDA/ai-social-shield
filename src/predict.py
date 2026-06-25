import pickle
import numpy as np
import urllib.request
import cv2
import easyocr
from transformers import pipeline

with open('models/account_model.pkl', 'rb') as f:
    account_model = pickle.load(f)

nlp_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

reader = easyocr.Reader(['en'])

def analyze_account(has_profile_pic, bio_length, followers, following, num_posts):
    features = np.array([[has_profile_pic, bio_length, followers, following, num_posts]])
    prob = account_model.predict_proba(features)[0][1]
    
    reasons = []
    if following > 0:
        ratio = followers / following
        if ratio < 0.1:
            reasons.append("Extremely low follower-to-following ratio.")
    if has_profile_pic == 0:
        reasons.append("Missing profile picture.")
    if num_posts < 3:
        reasons.append("Very low post activity.")
        
    return prob, reasons

def analyze_comment(text):
    text_low = text.lower()
    
    # 1. Pure English Spam Keywords
    eng_keywords = ['crypto', 'whatsapp', 'click link', 'dm me', 'invest', 'payout', 'free followers']
    
    # 2. Advanced Hinglish / Hindi Spam Keywords (Localization)
    hinglish_keywords = [
        'paisa kamao', 'ghar baithe', 'kamana', 'part time job', 
        'earn daily', 'rupaye', 'lakho kamao', 'link par jao', 
        'msg karo', 'biwi', 'paise', 'kamao', 'free me'
    ]
    
    # Check if any keyword matches
    has_eng_spam = any(kw in text_low for kw in eng_keywords)
    has_hin_spam = any(kw in text_low for kw in hinglish_keywords)
    
    # BERT Model Inference
    result = nlp_classifier(text)[0]
    base_score = 0.85 if result['label'] == 'NEGATIVE' else 0.15
    
    # Hybrid Combination Logic
    if has_eng_spam or has_hin_spam:
        base_score = min(0.99, base_score + 0.45)
        
    return base_score

def analyze_image_url(image_url):
    if not image_url:
        return 0.0
    try:
        resp = urllib.request.urlopen(image_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        results = reader.readtext(image)
        extracted_text = " ".join([res[1] for res in results]).lower()
        
        # Image me bhi Hinglish/English dono text check honge
        spam_words = ['earn money', 'work from home', 'crypto', 'payout', 'dm me', 'paisa kamao', 'ghar baithe', 'free']
        is_spam = any(word in extracted_text for word in spam_words)
        
        return 0.90 if is_spam else 0.10
    except:
        return 0.0

def hybrid_shield_detector(profile_data):
    prob_account, _ = analyze_account(
        profile_data["has_profile_pic"], 
        profile_data["bio_length"], 
        profile_data["followers"], 
        profile_data["following"], 
        profile_data["num_posts"]
    )
    
    comment_scores = [analyze_comment(c) for c in profile_data["comments"]]
    prob_comment = np.mean(comment_scores) if comment_scores else 0.0
    
    prob_image = analyze_image_url(profile_data["image_url"])
    
    final_score = (prob_account * 0.3) + (prob_comment * 0.4) + (prob_image * 0.3)
    
    threat_explanation = {
        "account": [],
        "comments": [],
        "image": []
    }
    
    return final_score, prob_account, prob_comment, prob_image, threat_explanation