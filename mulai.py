"""
mulai.py - LAUNCHER 1-KLIK untuk device umum / warnet / Colab
Cara pakai:
  Windows: klik 2x START_AGENT_WINDOWS.bat
  Linux  : ./START_AGENT_LINUX.sh
  Manual : python mulai.py

Yang kamu lakukan HANYA:
  1. Tempel MEMORY_URL + MEMORY_KEY (1x per sesi, tidak disimpan di PC umum)
  2. Duduk manis, sisanya AUTO: pull -> jalan -> push tiap step

Prinsip anti-hilang untuk device umum:
  - Tulis lokal dulu (tetap aman walau internet mati)
  - Coba push ke cloud tiap step (kalau gagal, coba lagi step berikut)
  - Saat keluar (Ctrl+C / error / selesai) -> push terakhir + bundle lokal
"""
import os
import sys
import time
import getpass
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def minta_key():
    # 1. Ambil dari env dulu (kalau ada, tidak tanya lagi)
    url = os.environ.get("MEMORY_URL", "").strip()
    key = os.environ.get("MEMORY_KEY", "").strip()

    # 2. Kalau kosong, tanya 1x (tidak disimpan permanen di device umum)
    if not url:
        print("")
        print("🔑 Masukkan API Key Cloud (1x saja per sesi)")
        print("   Contoh URL: https://xxxx.supabase.co/rest/v1/memory")
        print("   (Dapatkan 1x di HP/PC pribadi, gratis di supabase.com)")
        print("")
        url = input("📋 MEMORY_URL: ").strip()
    if not key:
        # getpass biar tidak terlihat di layar warnet
        try:
            key = getpass.getpass("🔒 MEMORY_KEY (ketikan disembunyikan): ").strip()
        except Exception:
            key = input("🔒 MEMORY_KEY: ").strip()

    os.environ["MEMORY_URL"] = url
    os.environ["MEMORY_KEY"] = key
    return url, key

def auto_pull():
    log("🔄 [1/3] Download otak terbaru dari cloud...")
    try:
        from memory_remote import pull_remote
        data = pull_remote(limit=1000)
        log(f"📦 Otak dimuat: {len(data)} pengalaman")
        return data
    except Exception as e:
        log(f"⚠️ pull gagal, pakai lokal saja: {e}")
        return []

def auto_push_terakhir(note="auto-save dari device umum"):
    # Push 1 baris terakhir + bundle via sync.py (tanpa login Google)
    try:
        from memory_remote import push_remote
        push_remote(note, meta={"auto": True, "device": os.environ.get("COMPUTERNAME", os.uname().nodename if hasattr(os, "uname") else "pc-umum")})
    except Exception as e:
        log(f"⚠️ push remote gagal (tetap aman lokal): {e}")
    try:
        import subprocess
        subprocess.run([sys.executable, "sync.py", "push", note], cwd=ROOT, check=False)
    except Exception:
        pass

def main():
    print("")
    print("================================")
    print(" 🧠 AI AGENT 1-KLIK - ANTI HILANG")
    print(" ================================")
    print("")

    url, key = minta_key()
    if not url or not key:
        print("⚠️ Key kosong, lanjut mode lokal saja (tetap aman, nanti bisa push).")

    auto_pull()

    # Tanya task singkat (boleh Enter untuk default)
    task = input("📝 Mau kerjakan apa? (Enter = belajar otomatis): ").strip() or "belajar otomatis"
    try:
        steps = input("🔢 Berapa step? (Enter = 100): ").strip() or "100"
        max_steps = int(steps)
    except Exception:
        max_steps = 100

    print("")
    log(f"🚀 Jalan: '{task}' target {max_steps} step")
    log("💡 Tips warnet: internet mati / PC mati = aman, ulangi 1-klik -> lanjut otomatis")
    print("")

    # Import agent asli kamu
    try:
        from memory_store import load_memory, add_experience
        from main_agent import save_checkpoint, load_checkpoint
    except Exception as e:
        log(f"❌ file inti hilang: {e}")
        return

    memory = load_memory()
    checkpoint = load_checkpoint()
    start = max(int(checkpoint.get("step", 0)), int(memory.get("total_steps", 0)))
    log(f"♻️ Lanjut dari pengalaman ke-{start} | pelajaran: {len(memory.get('lessons', []))}")

    step = start
    last_push = time.time()
    try:
        while step < start + max_steps:
            step += 1
            # --- KERJA AGENT (ganti dengan LLM kamu di persistent_agent.agent_think) ---
            lessons = memory.get("lessons", [])
            bekal = f"bekal {len(lessons)} pelajaran" if lessons else "mulai belajar"
            output = f"step-{step}: {task} dengan {bekal}"
            lesson = f"Pelajaran step {step}: cara cepat {task}" if step % 10 == 0 else ""

            # 1. Simpan lokal dulu (tahan internet mati)
            memory = add_experience(memory, f"{task} step {step}", output, lesson)
            save_checkpoint({"step": step, "data": [output], "last_update": str(datetime.now())})

            # 2. Coba push cloud tiap step (kalau gagal, tetap aman lokal)
            try:
                from memory_remote import push_remote
                # push tiap 5 step biar hemat kuota warnet
                if step % 5 == 0 or (time.time() - last_push > 120):
                    push_remote(f"{task} step {step}: {output}", meta={"step": step, "lesson": lesson})
                    last_push = time.time()
                    log(f"✅ step {step} + ☁️ cloud OK")
                else:
                    log(f"✅ step {step} selesai (lokal aman)")
            except Exception as e:
                log(f"✅ step {step} selesai (lokal aman, cloud nanti: {e})")

            time.sleep(0.5)

    except KeyboardInterrupt:
        log("⏸️ Berhenti manual, menyimpan terakhir...")
    except Exception as e:
        log(f"❌ Error: {e}, menyimpan dulu...")
    finally:
        log("🔄 [3/3] Auto-upload terakhir...")
        auto_push_terakhir(f"selesai {task} sampai step {step}")
        log(f"🏁 Aman! Total: {memory.get('total_steps')} pengalaman, {len(memory.get('lessons', []))} pelajaran")
        print("")
        print("✅ Boleh tutup / pindah device. Di device baru tinggal 1-klik lagi.")
        print("")

if __name__ == "__main__":
    main()
