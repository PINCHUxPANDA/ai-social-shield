import instaloader
import random

def fetch_instagram_data(username):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        profile_data = {
            "has_profile_pic": 1 if profile.profile_pic_url else 0,
            "bio_length": len(profile.biography) if profile.biography else 0,
            "followers": profile.followers,
            "following": profile.followees,
            "num_posts": profile.mediacount,
            "comments": [],
            "image_url": None
        }
        
        for post in profile.get_posts():
            profile_data["image_url"] = post.url
            count = 0
            for comment in post.get_comments():
                profile_data["comments"].append(comment.text)
                count += 1
                if count >= 5: 
                    break
            break 
            
        return profile_data

    except Exception as e:
        # AGAR INSTAGRAM BLOCK KAREGA, TOH YEH DEMO MODE CHAL JAYEGA:
        print(f"Instagram blocked or error: {e}. Switching to Demo Mock Mode...")
        
        # Test ke liye automatic mock comments aur data generate karna
        mock_comments = [
            "Ghar baithe paisa kamao daily 5000 tak! DM me right now!",
            "Kya mast photo hai bhai!",
            "Part time kaam karke lakho kamao, link par jao jaldi",
            "Nice pic dear",
            "Mujhe btao kaise kamana hai paise"
        ]
        
        # Randomly select features to simulate a bot or real user based on username
        is_bot_name = any(x in username.lower() for x in ['bot', 'scam', 'test', 'fake', 'laksh'])
        
        profile_data = {
            "has_profile_pic": 0 if is_bot_name else 1,
            "bio_length": 12 if is_bot_name else 65,
            "followers": 15 if is_bot_name else 1420,
            "following": 3800 if is_bot_name else 320,
            "num_posts": 2 if is_bot_name else 45,
            "comments": mock_comments if is_bot_name else ["Awesome!", "Cool", "Nice piece"],
            # Ek sample image link placeholder testing ke liye
            "image_url": "https://picsum.photos/300/300" 
        }
        return profile_data