#!/usr/bin/env python3
"""Post VIX breach alert to X with image attachment using tweepy"""

import os
import tweepy

# Load credentials from .env
env_path = os.path.expanduser('~/.openclaw/.env')
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

# Credentials
consumer_key = os.environ['X_CONSUMER_KEY']
consumer_secret = os.environ['X_CONSUMER_SECRET']
access_token = os.environ['X_ACCESS_TOKEN']
access_token_secret = os.environ['X_ACCESS_TOKEN_SECRET']

# Image path
image_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/vix-breach-architecture.png'

# Tweet text
tweet_text = "⚠️ VIX BREACH ALERT | VIX: 31.05 (Threshold: 18.00) | +13.16% | Automated execution flow triggered. Architecture diagram attached."

print("Authenticating with X API...")

# OAuth 1.0a authentication (required for posting tweets and uploading media)
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

try:
    # Verify credentials
    user = api.verify_credentials()
    print(f"Authenticated as: @{user.screen_name}")
    
    # Upload media
    print("Uploading media...")
    media = api.media_upload(image_path)
    print(f"Media uploaded. Media ID: {media.media_id_string}")
    
    # Post tweet with media
    print("Posting tweet...")
    tweet = api.update_status(status=tweet_text, media_ids=[media.media_id_string])
    
    print(f"\n✅ Tweet posted successfully!")
    print(f"Tweet ID: {tweet.id_str}")
    print(f"Post URL: https://x.com/{user.screen_name}/status/{tweet.id_str}")
    
except tweepy.TweepyException as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
