import json
from urllib import request, error

# TO THE USER: Fill in your Supabase details below to enable the global leaderboard!
# You can get these from your Supabase Project Settings -> API
SUPABASE_URL = "https://ysbnmdxkdblbzooozryo.supabase.co"
SUPABASE_KEY = "sb_publishable_zZ4_gcTU3Q6DO-EMzh1pMg_OsMGGYIH"

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
    
    try:
        req = request.Request(url, data=data, headers=headers, method="POST")
        with request.urlopen(req) as response:
            return response.status == 201
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
