#!/usr/bin/env python3
"""Generate audio using gTTS with retry logic"""

from gtts import gTTS
import os
import time

briefing_text = """Luxury Goods Sector Briefing. Consumer Spending in Emerging Markets. March 2026.

Executive Summary: The luxury goods sector continues to experience significant transformation, with emerging markets driving substantial global growth.

Key Market Dynamics: First, Emerging Markets Growth. Asia-Pacific remains dominant, particularly China, India, and Southeast Asia. Middle East showing renewed strength. Latin America recovering. Africa emerging as frontier market.

Second, Consumer Behavior. Digital-First Shopping: E-commerce penetration exceeds 40 percent. Social commerce driving discovery. Mobile-first shopping under age 40. Experience Over Ownership: Growing preference for luxury experiences. Quiet luxury trend gaining traction.

Third, Demographics. Generation Z and Millennials represent over 60 percent of luxury consumers. 200 million plus new luxury consumers expected by 2030.

Fourth, Category Performance. Personal Luxury Goods growing 8 to 12 percent annually. Luxury Beauty growing 15 to 20 percent. Fine Watches and Jewelry growing 10 to 15 percent. Luxury Hospitality growing 12 to 18 percent annually.

Strategic Implications: Opportunities include Digital Investment, Localization, Entry-Point Products, and Experience Economy. Risks include Economic Volatility, Counterfeit Markets, and Regulatory Changes.

Recommendations: Focus on top 5 emerging markets. Accelerate e-commerce. Develop market-specific collections. Explore local collaborations. Embed ESG considerations.

End of briefing."""

output_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/luxury_goods_briefing.mp3'

print("Generating audio with gTTS...")
print(f"Text length: {len(briefing_text)} characters")

max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1} of {max_retries}...")
        tts = gTTS(text=briefing_text, lang='en')
        tts.save(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            size = os.path.getsize(output_path)
            print(f"\n✓ SUCCESS!")
            print(f"  File: {output_path}")
            print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")
            break
    except Exception as e:
        print(f"  Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            print("  Waiting 5 seconds before retry...")
            time.sleep(5)
else:
    print("\n✗ All attempts failed")
    if os.path.exists(output_path):
        os.remove(output_path)
