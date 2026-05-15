import json
from urllib import request, error
import sys
import platform
import random
import asyncio

# TO THE USER: Fill in your Supabase details below to enable the global leaderboard!
# You can get these from your Supabase Project Settings -> API
SUPABASE_URL = "https://ysbnmdxkdblbzooozryo.supabase.co"
SUPABASE_KEY = "sb_publishable_zZ4_gcTU3Q6DO-EMzh1pMg_OsMGGYIH"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1504734664211042438/J8_2mhuJM3fi-ybm_DtAqVCgqIyo7rPv8sfFrFdcZus56mL9ngFDReS9hQOQXR3jVcr1"

def send_to_discord(name, score, level):
    """Sends a formatted score card to Discord via Webhook"""
    if not DISCORD_WEBHOOK_URL: return
    
    payload = {
        "embeds": [{
            "title": "🚀 NEW HIGH SCORE RECORDED!",
            "color": 5814783, # Cyan
            "fields": [
                {"name": "Pilot", "value": f"**{name}**", "inline": True},
                {"name": "Score", "value": f"**{score}**", "inline": True},
                {"name": "Difficulty", "value": level, "inline": True}
            ],
            "footer": {"text": "Flappy Space: Enhanced Edition"}
        }]
    }
    
    if sys.platform == "emscripten":
        # Non-blocking web fetch
        js_code = f"""
        fetch('{DISCORD_WEBHOOK_URL}', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({json.dumps(payload)})
        }});
        """
        try:
            platform.window.eval(js_code)
        except: pass
        return

    try:
        req = request.Request(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"Discord error: {e}")

def submit_score(name, score, level):
    """Submits a score to Supabase via REST API"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Database not configured. Score not saved.")
        return False
        
    url = f"{SUPABASE_URL}/rest/v1/leaderboard"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    data = json.dumps({
        "username": name,
        "score": score,
        "level": level
    }).encode("utf-8")
    
    if sys.platform == "emscripten":
        # Create the payload specifically for this call
        payload = {
            "embeds": [{
                "title": "🚀 NEW HIGH SCORE RECORDED!",
                "color": 5814783,
                "fields": [
                    {"name": "Pilot", "value": f"**{name}**", "inline": True},
                    {"name": "Score", "value": f"**{score}**", "inline": True},
                    {"name": "Difficulty", "value": level, "inline": True}
                ],
                "footer": {"text": "Flappy Space: Enhanced Edition"}
            }]
        }
        
        # Non-blocking web fetch for Supabase AND Discord separately to be safe
        js_code = f"""
        fetch('{url}', {{
            method: 'POST',
            headers: {{ 
                'apikey': '{SUPABASE_KEY}',
                'Authorization': 'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{
                "username": "{name}",
                "score": {score},
                "level": "{level}"
            }})
        }});
        
        fetch('{DISCORD_WEBHOOK_URL}', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({json.dumps(payload)})
        }});
        """
        try:
            platform.window.eval(js_code)
        except Exception as e:
            print(f"Web Submit Error: {e}")
        return True

    try:
        req = request.Request(url, data=data, headers=headers, method="POST")
        with request.urlopen(req) as response:
            if response.status == 201:
                # Also send to Discord!
                send_to_discord(name, score, level)
                return True
            return False
    except Exception as e:
        print(f"Error submitting score: {e}")
        return False

async def async_get_top_scores(level=None, limit=10):
    """Asynchronously fetches top scores from Supabase for Web"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
        
    query = f"select=*&order=score.desc&limit={limit*2}"
    if level:
        query += f"&level=eq.{level}"
        
    url = f"{SUPABASE_URL}/rest/v1/leaderboard?{query}"
    
    # Use a unique global variable name to avoid conflicts
    js_var = f"lb_data_{random.randint(0, 10000)}"
    js_code = f"""
    window.{js_var} = null;
    fetch('{url}', {{
        headers: {{
            'apikey': '{SUPABASE_KEY}',
            'Authorization': 'Bearer {SUPABASE_KEY}'
        }}
    }}).then(r => r.json())
      .then(data => {{ window.{js_var} = data; }})
      .catch(e => {{ window.{js_var} = []; console.error(e); }});
    """
    try:
        platform.window.eval(js_code)
        
        # Poll for the result (max 5 seconds)
        for _ in range(50):
            data = platform.window.get(js_var)
            if data is not None:
                # Filter unique
                unique_data = {}
                for entry in data:
                    user = entry.get('username')
                    if not user: continue
                    score = entry.get('score', 0)
                    if user not in unique_data or score > unique_data[user]['score']:
                        unique_data[user] = entry
                
                sorted_data = sorted(unique_data.values(), key=lambda x: x.get('score', 0), reverse=True)
                return sorted_data[:limit]
            await asyncio.sleep(0.1)
            
        return []
    except Exception as e:
        print(f"Async fetch error: {e}")
        return []

def get_top_scores(level=None, limit=10):
    """Fetches top scores from Supabase, optionally filtered by level"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
        
    query = f"select=*&order=score.desc&limit={limit}"
    if level:
        query += f"&level=eq.{level}"
        
    url = f"{SUPABASE_URL}/rest/v1/leaderboard?{query}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        req = request.Request(url, headers=headers, method="GET")
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching scores: {e}")
        return []
