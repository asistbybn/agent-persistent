"""
AI Agent Persistent Runner - anti hilang saat runtime berhenti
Cara kerja:
- Semua state disimpan ke disk lokal + GCS Bucket / Drive
- Setiap loop autosave, bisa resume otomatis
- Tahan restart, preempted, Colab disconnect
"""
import os
import json
import time
import pickle
from datetime import datetime

# === KONFIGURASI ===
CHECKPOINT_LOCAL = "./data/checkpoint.pkl"
STATE_JSON = "./data/state.json"
SAVE_EVERY_N_STEPS = 5  # simpan tiap 5 langkah
SAVE_EVERY_SECONDS = 300  # + tiap 5 menit

# GCS (isi jika pakai Compute Engine / Vertex)
# contoh: gs://nama-bucket-agent-kamu
GCS_BUCKET = os.getenv("GCS_BUCKET", "")  # set env: export GCS_BUCKET=gs://xxx
GCS_PATH = os.getenv("GCS_PATH", "checkpoint.pkl")

# Drive (isi jika pakai Colab)
# contoh: /content/drive/MyDrive/project-agent/checkpoint.pkl
DRIVE_CHECKPOINT = os.getenv("DRIVE_CHECKPOINT", "")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def ensure_dir():
    os.makedirs(os.path.dirname(CHECKPOINT_LOCAL) or ".", exist_ok=True)

def save_checkpoint(state: dict):
    ensure_dir()
    # 1. lokal
    with open(CHECKPOINT_LOCAL, "wb") as f:
        pickle.dump(state, f)
    with open(STATE_JSON, "w") as f:
        json.dump(state, f, indent=2, default=str)
    log(f"checkpoint lokal tersimpan step={state.get('step')}")

    # 2. Google Drive (Colab)
    if DRIVE_CHECKPOINT:
        try:
            import shutil
            os.makedirs(os.path.dirname(DRIVE_CHECKPOINT), exist_ok=True)
            shutil.copy(CHECKPOINT_LOCAL, DRIVE_CHECKPOINT)
            log(f"backup ke Drive: {DRIVE_CHECKPOINT}")
        except Exception as e:
            log(f"gagal backup Drive: {e}")

    # 3. GCS Bucket (Cloud)
    if GCS_BUCKET:
        try:
            from google.cloud import storage
            bucket_name = GCS_BUCKET.replace("gs://", "").strip("/")
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(GCS_PATH)
            blob.upload_from_filename(CHECKPOINT_LOCAL)
            log(f"backup ke GCS: gs://{bucket_name}/{GCS_PATH}")
        except Exception as e:
            log(f"gagal backup GCS: {e} (pastikan google-cloud-storage terinstall + auth)")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_LOCAL):
        try:
            with open(CHECKPOINT_LOCAL, "rb") as f:
                state = pickle.load(f)
            log(f"resume dari lokal step={state.get('step')}")
            return state
        except Exception as e:
            log(f"checkpoint lokal rusak: {e}")

    if DRIVE_CHECKPOINT and os.path.exists(DRIVE_CHECKPOINT):
        try:
            import shutil
            ensure_dir()
            shutil.copy(DRIVE_CHECKPOINT, CHECKPOINT_LOCAL)
            with open(CHECKPOINT_LOCAL, "rb") as f:
                state = pickle.load(f)
            log(f"resume dari Drive step={state.get('step')}")
            return state
        except Exception as e:
            log(f"gagal load Drive: {e}")

    if GCS_BUCKET:
        try:
            from google.cloud import storage
            bucket_name = GCS_BUCKET.replace("gs://", "").strip("/")
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(GCS_PATH)
            if blob.exists():
                ensure_dir()
                blob.download_to_filename(CHECKPOINT_LOCAL)
                with open(CHECKPOINT_LOCAL, "rb") as f:
                    state = pickle.load(f)
                log(f"resume dari GCS step={state.get('step')}")
                return state
        except Exception as e:
            log(f"gagal load GCS: {e}")

    log("mulai dari awal (tidak ada checkpoint)")
    return {"step": 0, "data": [], "started_at": str(datetime.now())}

def your_agent_work(step: int, state: dict):
    time.sleep(2)
    return f"hasil-step-{step}"

def main(max_steps=1000):
    state = load_checkpoint()
    step = int(state.get("step", 0))
    last_time_save = time.time()
    log(f"agent jalan mulai step={step} target={max_steps}")
    try:
        while step < max_steps:
            step += 1
            result = your_agent_work(step, state)
            state["data"].append(result)
            state["step"] = step
            state["last_update"] = str(datetime.now())
            should_save = (step % SAVE_EVERY_N_STEPS == 0) or (time.time() - last_time_save > SAVE_EVERY_SECONDS)
            if should_save:
                save_checkpoint(state)
                last_time_save = time.time()
            else:
                log(f"... step {step} selesai: {result}")
    except KeyboardInterrupt:
        log("dihentikan manual, menyimpan...")
        save_checkpoint(state)
    except Exception as e:
        log(f"error: {e}, menyimpan checkpoint terakhir...")
        save_checkpoint(state)
        raise
    else:
        save_checkpoint(state)
        log("semua step selesai!")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--max-steps", type=int, default=1000)
    args = p.parse_args()
    main(max_steps=args.max_steps)
