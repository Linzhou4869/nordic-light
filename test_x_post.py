#!/usr/bin/env python3
"""Quick test of X API credentials"""

import os
import tweepy

env_path = os.path.expanduser('~/.openclaw/.env')
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

print("=" * 60)
print("X API CREDENTIAL TEST")
print("=" * 60)
print(f"Consumer Key: {os.environ.get('X_CONSUMER_KEY', 'NOT FOUND')}")
print(f"Consumer Secret: {os.environ.get('X_CONSUMER_SECRET', 'NOT FOUND')}")
print(f"Access Token: {os.environ.get('X_ACCESS_TOKEN', 'NOT FOUND')}")
print(f"Access Secret: {os.environ.get('X_ACCESS_TOKEN_SECRET', 'NOT FOUND')}")
print()

auth = tweepy.OAuth1UserHandler(
    os.environ['X_CONSUMER_KEY'],
    os.environ['X_CONSUMER_SECRET'],
    os.environ['X_ACCESS_TOKEN'],
    os.environ['X_ACCESS_TOKEN_SECRET']
)
api = tweepy.API(auth, timeout=10)

try:
    print("Attempting to verify credentials...")
    user = api.verify_credentials()
    print(f"SUCCESS: Authenticated as @{user.screen_name}")
except tweepy.TweepyException as e:
    print(f"FAILED: {type(e).__name__}")
    print(f"Error: {e}")
    print()
    print("This is expected with test credentials.")
    print("Real X API credentials are required for live posting.")
