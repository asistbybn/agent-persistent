"""
persistent_agent.py - AI Agent yang TIDAK PERNAH hilang + terus belajar
- Pengalaman disimpan di memory_store.py (append-only)
- Checkpoint + memory auto-sync ke Drive / GCS tiap langkah
- Kalau runtime mati -> jalankan lagi, otomatis lanjut dari pengalaman terakhir
- Kamu sudah install 3x mulai dari nol? Dengan ini install cukup 1x selamanya.

Cara pakai Colab (cukup 1 cell, run ulang kalau putus):
  from google.colab import drive; drive.mount('/content/drive')
  import os
  os.environ["DRIVE_MEMORY"]="/content/drive/MyDrive/project-agent/memory.json"
  os.environ["DRIVE_CHECKPOINT"]="/content/drive/MyDrive/project-agent/checkpoint.pkl"
  !python agent-persistent/persistent_agent.py --max-steps 1000

Cara pakai VM permanen:
  export GCS_BUCKET=gs://nama-bucket-kamu
  python agent-persistent/persistent_agent.py --max-steps 10000
"""
import os
import time
import argparse
from datetime import datetime
from memory_store import load_memory, add_experience, save_memory

# biar bisa run dari root atau dari folder agent-persistent
try:
    from main_agent import save_checkpoint, load_checkpoint
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from main_agent import save_checkpoint, load_checkpoint

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def agent_think(step, memory, user_task="belajar otomatis"):
    """
    GANTI INI dengan otak agent kamu yang asli:
    - panggil LLM / LangChain / CrewAI / API kamu di sini
    - contoh sederhana: dia ingat pelajaran lama untuk bikin output baru makin pintar
    """
    lessons = memory.get("lessons", [])
    total = memory.get("total_steps", 0)
    # simulasi makin pintar karena ingat pelajaran
    knowledge = f"bekal {len(lessons)} pelajaran" if lessons else "mulai belajar"
    output = f"step-{step}: kerjakan '{user_task}' dengan {knowledge} (total pengalaman {total+1})"
    lesson = ""
    # tiap 10 step buat 1 pelajaran baru biar kelihatan nambah pintar
    if step % 10 == 0:
        lesson = f"Pelajaran dari step {step}: cara lebih cepat kerjakan {user_task}"
    time.sleep(1)  # simulasi kerja, hapus kalau pakai LLM asli
    return output, lesson

def main(max_steps=1000, task="belajar otomatis"):
    log("🚀 Persistent Agent mulai...")
    memory = load_memory()
    checkpoint = load_checkpoint()
    start_step = int(checkpoint.get("step", 0))
    # sinkron: kalau memory lebih baru dari checkpoint, pakai memory
    if int(memory.get("total_steps", 0)) > start_step:
        start_step = int(memory.get("total_steps", 0))

    log(f"♻️ lanjut dari pengalaman ke-{start_step} | total pelajaran: {len(memory.get('lessons',[]))}")
    log(f"📚 3 pelajaran terakhir: {memory.get('lessons',[])[-3:]}")

    step = start_step
    try:
        while step < max_steps:
            step += 1
            output, lesson = agent_think(step, memory, task)

            # 1. tambah pengalaman (auto-save ke lokal+Drive+GCS)
            memory = add_experience(memory, f"{task} step {step}", output, lesson)

            # 2. update checkpoint teknis (untuk resume cepat)
            save_checkpoint({"step": step, "data": [output], "last_update": str(datetime.now())})

            log(f"✅ step {step} selesai: {output[:80]}")
            if lesson:
                log(f"🧠 +1 pelajaran baru: {lesson}")

    except KeyboardInterrupt:
        log("⏸️ dihentikan manual, pengalaman sudah aman tersimpan.")
        save_memory(memory)
        save_checkpoint({"step": step, "data": [], "last_update": str(datetime.now())})
    except Exception as e:
        log(f"❌ error: {e}, menyimpan dulu biar tidak hilang...")
        save_memory(memory)
        save_checkpoint({"step": step, "data": [], "last_update": str(datetime.now())})
        raise
    else:
        log(f"🏁 selesai sampai {step}. Total pengalaman: {memory.get('total_steps')}, pelajaran: {len(memory.get('lessons',[]))}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--max-steps", type=int, default=1000)
    p.add_argument("--task", type=str, default="belajar otomatis")
    args = p.parse_args()
    main(max_steps=args.max_steps, task=args.task)
