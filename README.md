# Anti-hilang Google Cloud - Panduan Cepat

## Kenapa runtime berhenti & data hilang?
- Colab gratis: putus 90 mnt idle, max ~12 jam reset total
- Spot / Preemptible VM: bisa direbut Google kapan saja (24 jam max)
- Semua file di /content atau /tmp itu SEMENTARA

Prinsip: COMPUTE sementara, STORAGE permanen.

## Solusi 1 baris per platform

### A. Kalau pakai Colab (gratis)
1. Mount Drive di awal notebook:
```python
from google.colab import drive
drive.mount('/content/drive')
```
2. Set env lalu jalan:
```python
import os
os.environ["DRIVE_CHECKPOINT"] = "/content/drive/MyDrive/project-agent/checkpoint.pkl"
!python agent-persistent/main_agent.py --max-steps 1000
```
3. Kalau putus, RUN ULANG cell di atas -> otomatis resume dari step terakhir.

### B. Kalau pakai Compute Engine VM (permanen)
1. JANGAN pakai Spot/Preemptible untuk agent lama. Pakai e2-medium standard.
2. Buat bucket:
```bash
gsutil mb gs://nama-bucket-agent-kamu
export GCS_BUCKET=gs://nama-bucket-agent-kamu
```
3. Jalan di background biar tahan SSH putus:
```bash
chmod +x agent-persistent/run.sh
./agent-persistent/run.sh
# cek log
tail -f agent.log
# balik lagi nanti:
tmux attach -t agent
```

### C. Biar VM restart otomatis jalan lagi (systemd)
```bash
sudo cp agent-persistent/agent.service /etc/systemd/system/agent.service
sudo systemctl enable agent
sudo systemctl start agent
sudo systemctl status agent
```

## File di folder ini
- main_agent.py = loop agent + autosave tiap 5 langkah / 5 menit + resume otomatis
- colab_snippet.py = tempel ke Colab, anti javascript idle + autosave Drive
- run.sh = jalan tmux + nohup + upload ke GCS
- requirements.txt = dependensi
- agent.service = auto-start saat VM reboot
