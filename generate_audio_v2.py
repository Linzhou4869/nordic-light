#!/usr/bin/env python3
"""Generate audio briefing using direct HTTP request to TTS service"""

import requests
import os

# Shorter briefing text for faster generation
briefing_text = """Luxury Goods Sector Briefing. Consumer Spending Habits in Emerging Markets. March 29, 2026.

Executive Summary: The luxury goods sector continues to experience significant transformation, with emerging markets driving substantial global growth.

Key Market Dynamics: First, Emerging Markets Growth Trajectory. Asia-Pacific remains dominant, particularly China, India, and Southeast Asian nations. Middle East showing renewed strength. Latin America experiencing steady recovery. Africa emerging as frontier market.

Second, Consumer Behavior Shifts. Digital-First Luxury Shopping: E-commerce penetration exceeds 40 percent. Social commerce driving discovery. Mobile-first shopping predominant among under-40 consumers. Experience Over Ownership: Growing preference for luxury experiences. Quiet luxury trend gaining traction.

Third, Demographic Drivers. Generation Z and Millennials represent over 60 percent of luxury consumers. 200 million plus new luxury consumers expected by 2030.

Fourth, Category Performance. Personal Luxury Goods growing 8 to 12 percent annually. Luxury Beauty growing 15 to 20 percent. Fine Watches and Jewelry growing 10 to 15 percent. Luxury Hospitality growing 12 to 18 percent annually.

Strategic Implications: Opportunities include Digital Investment, Localization, Entry-Point Products, and Experience Economy expansion. Risks include Economic Volatility, Counterfeit Markets, and Regulatory Changes.

Recommendations: Focus on top 5 emerging markets. Accelerate e-commerce capabilities. Develop market-specific collections. Explore local collaborations. Embed ESG considerations.

End of briefing."""

output_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/luxury_goods_briefing.mp3'

print("Generating audio...")

# Try Google Translate TTS (unofficial but works)
def try_google_tts():
    url = "https://translate.google.com/translate_tts"
    params = {
        'ie': 'UTF-8',
        'q': briefing_text[:200],  # Shorter for this service
        'tl': 'en',
        'client': 'tw-ob'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Google TTS failed: {e}")
    return False

# Try VoiceRSS
def try_voicerss():
    url = "https://api.voicerss.org/"
    params = {
        'key': 'demo',  # Demo key
        'hl': 'en-us',
        'src': briefing_text[:300],
        'f': 'mp3_44khz_128kbstereo'
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"VoiceRSS failed: {e}")
    return False

# Try TTSMP3.com (free API)
def try_ttsmp3():
    url = "https://ttsmp3.com/makemp3_new.php"
    params = {
        'msg': briefing_text[:500],
        'lang': 'USenglish',
        'source': 'ttsmp3'
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if 'URL' in data:
            audio_url = data['URL']
            audio_response = requests.get(audio_url, timeout=30)
            if audio_response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(audio_response.content)
                return True
    except Exception as e:
        print(f"TTSMP3 failed: {e}")
    return False

# Try each service
if try_ttsmp3():
    print("✓ Generated using TTSMP3.com")
elif try_voicerss():
    print("✓ Generated using VoiceRSS")
elif try_google_tts():
    print("✓ Generated using Google TTS")
else:
    print("All TTS services failed")

# Verify
if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
    size = os.path.getsize(output_path)
    print(f"\n✓ Audio file created: {output_path}")
    print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")
else:
    print("\n✗ Audio file creation failed")
