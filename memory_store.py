"""
memory_store.py - Otak permanen AI Agent
- Semua pengalaman disimpan append-only, tidak pernah di-reset ke nol
- Auto-sync: lokal -> Google Drive -> GCS Bucket
- Kalau runtime mati, load terakhir dan lanjut tambah ilmu
"""
import os
import json
import shutil
from datetime import datetime

MEMORY_LOCAL = "./data/memory.json"
DRIVE_MEMORY = os.getenv("DRIVE_MEMORY", "")
GCS_BUCKET = os.getenv("GCS_BUCKET", "")
GCS_MEMORY_PATH = os.getenv("GCS_MEMORY_PATH", "memory.json")

def _now():
    return datetime.now().isoformat()

def default_memory():
    return {
        "version": 2,
        "created_at": _now(),
        "total_steps": 0,
        "experiences": [],
        "lessons": [],
        "skills": {},
        "last_update": _now()
    }

def ensure_dir(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def load_memory():
    if os.path.exists(MEMORY_LOCAL):
        try:
            with open(MEMORY_LOCAL, "r") as f:
                m = json.load(f)
            print(f"memory dimuat dari lokal: {len(m.get('experiences',[]))} pengalaman, {len(m.get('lessons',[]))} pelajaran", flush=True)
            return m
        except Exception as e:
            print(f"memory lokal rusak: {e}, coba backup...")

    if DRIVE_MEMORY and os.path.exists(DRIVE_MEMORY):
        try:
            ensure_dir(MEMORY_LOCAL)
            shutil.copy(DRIVE_MEMORY, MEMORY_LOCAL)
            with open(MEMORY_LOCAL, "r") as f:
                m = json.load(f)
            print(f"memory dipulihkan dari Drive: {len(m.get('experiences',[]))} pengalaman", flush=True)
            return m
        except Exception as e:
            print(f"gagal load Drive memory: {e}")

    if GCS_BUCKET:
        try:
            from google.cloud import storage
            bucket_name = GCS_BUCKET.replace("gs://", "").strip("/")
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(GCS_MEMORY_PATH)
            if blob.exists():
                ensure_dir(MEMORY_LOCAL)
                blob.download_to_filename(MEMORY_LOCAL)
                with open(MEMORY_LOCAL, "r") as f:
                    m = json.load(f)
                print(f"memory dipulihkan dari GCS: {len(m.get('experiences',[]))} pengalaman", flush=True)
                return m
        except Exception as e:
            print(f"gagal load GCS memory: {e}")

    print("memory baru dibuat (pertama kali). Selanjutnya akan terus bertambah, tidak reset.", flush=True)
    return default_memory()

def save_memory(mem):
    mem["last_update"] = _now()
    ensure_dir(MEMORY_LOCAL)
    with open(MEMORY_LOCAL, "w") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)
    print(f"memory tersimpan lokal: total_steps={mem.get('total_steps')} exp={len(mem.get('experiences',[]))}", flush=True)

    if DRIVE_MEMORY:
        try:
            ensure_dir(DRIVE_MEMORY)
            shutil.copy(MEMORY_LOCAL, DRIVE_MEMORY)
            print(f"backup memory ke Drive", flush=True)
        except Exception as e:
            print(f"gagal backup Drive: {e}")

    if GCS_BUCKET:
        try:
            from google.cloud import storage
            bucket_name = GCS_BUCKET.replace("gs://", "").strip("/")
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(GCS_MEMORY_PATH)
            blob.upload_from_filename(MEMORY_LOCAL)
            print(f"backup memory ke GCS gs://{bucket_name}/{GCS_MEMORY_PATH}", flush=True)
        except Exception as e:
            print(f"gagal backup GCS: {e}")

def add_experience(mem, user_input, agent_output, lesson=""):
    mem["total_steps"] = int(mem.get("total_steps", 0)) + 1
    exp = {
        "step": mem["total_steps"],
        "time": _now(),
        "input": user_input,
        "output": agent_output,
        "lesson": lesson
    }
    mem["experiences"].append(exp)
    if lesson and lesson not in mem.get("lessons", []):
        mem["lessons"].append(lesson)
    if len(mem["experiences"]) > 1000:
        archive_path = "./data/memory_archive.jsonl"
        ensure_dir(archive_path)
        with open(archive_path, "a") as af:
            for old in mem["experiences"][:500]:
                af.write(json.dumps(old, ensure_ascii=False) + "\n")
        mem["experiences"] = mem["experiences"][-500:]
        print("500 pengalaman lama di-archive, pelajaran tetap disimpan")
    save_memory(mem)
    return mem
