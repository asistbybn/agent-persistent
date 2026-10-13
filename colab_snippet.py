# Tempel di cell pertama Colab kamu
# 1. Anti-disconnect JS (klik otomatis tiap 60 detik agar tidak idle)
# 2. Mount Drive + resume otomatis

from google.colab import drive
import os
drive.mount('/content/drive')

os.environ["DRIVE_CHECKPOINT"] = "/content/drive/MyDrive/project-agent/checkpoint.pkl"

# --- keep alive JS: jalankan di cell dengan %%javascript ---
# Tempel manual di cell baru:
# %%javascript
# function ClickConnect(){
#   console.log("keep alive...");
#   document.querySelector("colab-toolbar-button#connect")?.click();
# }
# setInterval(ClickConnect, 60000)

print("✅ Drive mounted. Jalankan agent:")
print("!python agent-persistent/main_agent.py --max-steps 1000")
print("Kalau runtime putus, RUN ULANG 2 cell ini -> resume otomatis.")
