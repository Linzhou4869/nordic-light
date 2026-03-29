#!/usr/bin/env python3
"""Convert luxury goods briefing to audio using ElevenLabs"""

import requests
import os

# ElevenLabs configuration
API_KEY = os.environ.get('ELEVENLABS_API_KEY')
VOICE_ID = 'Rachel'  # Professional, clear voice good for briefings

# Voice mapping for ElevenLabs
voices = {
    'Rachel': '21m00Tcm4TlvDq8ikWAM',  # Professional, warm
    'Adam': 'pNInz6obpgDQGcFmaJgB',    # Authoritative
    'Antoni': 'ErXwobaYiN019PkySvjV',   # Clear, professional
}

# Briefing content
briefing_text = """
Luxury Goods Sector Briefing. Consumer Spending Habits in Emerging Markets. March 29, 2026.

Executive Summary: The luxury goods sector continues to experience significant transformation, with emerging markets driving substantial global growth.

Key Market Dynamics:

First, Emerging Markets Growth Trajectory. Asia-Pacific remains dominant, particularly China, India, and Southeast Asian nations. Middle East showing renewed strength. Latin America experiencing steady recovery. Africa emerging as frontier market.

Second, Consumer Behavior Shifts. Digital-First Luxury Shopping: E-commerce penetration exceeds 40 percent. Social commerce driving discovery. Mobile-first shopping predominant among under-40 consumers.

Experience Over Ownership: Growing preference for luxury experiences including travel, dining, and events. Quiet luxury trend gaining traction. Sustainability becoming a purchase criterion.

Third, Demographic Drivers. Generation Z and Millennials represent over 60 percent of luxury consumers. Higher spending propensity relative to income. 200 million plus new luxury consumers expected by 2030.

Fourth, Category Performance. Personal Luxury Goods growing 8 to 12 percent annually. Luxury Beauty growing 15 to 20 percent. Fine Watches and Jewelry growing 10 to 15 percent. Luxury Hospitality growing 12 to 18 percent annually.

Strategic Implications: Opportunities include Digital Investment, Localization, Entry-Point Products, and Experience Economy expansion. Risks include Economic Volatility, Counterfeit Markets, Regulatory Changes, and Generational Shifts.

Recommendations: Focus on top 5 emerging markets. Accelerate e-commerce capabilities. Develop market-specific collections. Explore local collaborations. Embed ESG considerations.

End of briefing.
"""

output_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/luxury_goods_briefing.mp3'

print("Generating audio with ElevenLabs...")

# ElevenLabs TTS API endpoint
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voices['Rachel']}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": API_KEY
}

data = {
    "text": briefing_text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"Audio file saved to: {output_path}")
    print("Attempting to play audio...")
else:
    print(f"Error: {response.status_code} - {response.text}")
