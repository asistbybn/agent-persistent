"""
auto.py - Jalan + Auto-Upload khusus kecerdasan saja
Dipakai setelah pemakaian, otomatis push hanya:
  brain/, skills/, tools/, memory.jsonl, *.py inti

Cara pakai di PC mana pun:
  python auto.py
  python auto.py --steps 1000
"""
import subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).parent

steps = "1000"
if "--steps" in sys.argv:
    try:
        steps = sys.argv[sys.argv.index("--steps")+1]
    except: pass

print("⏳ Memulai agent...")
print("🔄 [1/3] Download otak terbaru...")
subprocess.run([sys.executable, "sync.py", "pull"], cwd=ROOT)

print("🔄 [2/3] Menjalankan agent...")
subprocess.run([sys.executable, "persistent_agent.py", "--max-steps", steps], cwd=ROOT)

print("🔄 [3/3] Auto-upload kecerdasan + skill + tools...")
subprocess.run([sys.executable, "sync.py", "push", "auto-upload setelah pemakaian"], cwd=ROOT)

print("✅ Selesai - otak v baru sudah ter-upload, di PC lain tinggal pull")
