"""memory_remote.py - Otak tanpa login Google (Supabase/Firebase via URL+KEY).
Ganti DRIVE/GCS mount dengan HTTP request, cocok untuk pindah Windows/Linux/Colab.
"""
import os, json, urllib.request, urllib.parse, time
from pathlib import Path

MEMORY_URL = os.environ.get("MEMORY_URL", "")  # ex: https://xxxx.supabase.co/rest/v1/memory
MEMORY_KEY = os.environ.get("MEMORY_KEY", "")
LOCAL_MEMORY = Path(__file__).parent / "memory.jsonl"

def _headers():
    return {
        "apikey": MEMORY_KEY,
        "Authorization": f"Bearer {MEMORY_KEY}",
        "Content-Type": "application/json",
    }

def pull_remote(limit=1000):
    """Download memory terbaru tanpa login Google, simpan ke memory.jsonl"""
    if not MEMORY_URL or not MEMORY_KEY:
        print("⚠️ MEMORY_URL/KEY belum diset, pakai lokal saja")
        return load_local()
    try:
        url = f"{MEMORY_URL}?select=*&order=id.desc&limit={limit}"
        req = urllib.request.Request(url, headers=_headers())
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        # simpan append-only lokal
        with open(LOCAL_MEMORY, "w", encoding="utf-8") as f:
            for row in reversed(data):
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"📦 memory loaded: {len(data)} pengalaman dari remote (tanpa login)")
        return data
    except Exception as e:
        print(f"⚠️ pull remote gagal: {e}, fallback lokal")
        return load_local()

def push_remote(text, meta=None):
    """Upload 1 pengalaman baru tanpa login"""
    row = {"text": text, "meta": meta or {}, "ts": time.time()}
    # selalu append lokal dulu (tidak pernah hilang)
    with open(LOCAL_MEMORY, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    if not MEMORY_URL or not MEMORY_KEY:
        return row
    try:
        data = json.dumps(row).encode()
        req = urllib.request.Request(MEMORY_URL, data=data, headers=_headers(), method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
        print("✅ push remote OK")
    except Exception as e:
        print(f"⚠️ push remote gagal (tetap aman lokal): {e}")
    return row

def load_local():
    if not LOCAL_MEMORY.exists():
        return []
    rows = []
    with open(LOCAL_MEMORY, encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except: pass
    print(f"📦 memory loaded: {len(rows)} pengalaman lokal")
    return rows

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "pull":
        pull_remote()
    elif len(sys.argv) > 2 and sys.argv[1] == "push":
        push_remote(" ".join(sys.argv[2:]))
    else:
        print("pakai: python memory_remote.py pull | push <teks>")
