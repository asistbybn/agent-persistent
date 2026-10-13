#!/bin/bash
# START_AGENT_LINUX.sh - 1 perintah langsung jalan (Linux / Ubuntu / Colab)
# Yang kamu lakukan: ./START_AGENT_LINUX.sh -> tempel MEMORY_URL + MEMORY_KEY -> Enter
# Sisanya AUTO: pull -> jalan -> push tiap step
set -e
cd "$(dirname "$0")"

echo ""
echo "================================"
echo " AI AGENT 1-KLIK (Linux)"
echo "================================"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 belum ada. Install: sudo apt install python3 python3-pip -y"
  exit 1
fi

echo "[AUTO] cek kebutuhan..."
pip3 install -q -r requirements.txt 2>/dev/null || pip install -q -r requirements.txt 2>/dev/null || true

echo "[AUTO] download otak terbaru..."
python3 sync.py pull 2>/dev/null || true

echo ""
echo "[JALAN] tinggal tempel API key 1x..."
python3 mulai.py || python mulai.py

echo ""
echo "Selesai - otak sudah auto-upload ke cloud"
