import json
from urllib import request, error
import sys
import platform

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
        # Non-blocking web fetch for Supabase
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
        }}).then(r => {{ 
            if(r.ok) {{
                // After successful submit, send to discord
                fetch('{DISCORD_WEBHOOK_URL}', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({json.dumps(payload)})
                }});
            }}
        }});
        """
        try:
            platform.window.eval(js_code)
        except: pass
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
