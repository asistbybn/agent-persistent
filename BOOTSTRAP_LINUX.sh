#!/bin/bash
# BOOTSTRAP_LINUX.sh - FILE KECIL untuk dibawa di HP / catatan (2 KB)
set -e
echo ""
echo "================================"
echo " AMBIL AGENT DARI CLOUD"
echo "================================"
echo ""
AGENT_REPO="${AGENT_REPO:-asistbybn/agent-persistent}"
echo "[1/3] Download dari github.com/$AGENT_REPO ..."
if [ -d "agent-persistent" ]; then
  cd agent-persistent
  git pull || true
  cd ..
else
  if command -v git >/dev/null 2>&1; then
    git clone https://github.com/$AGENT_REPO.git
  else
    echo "git tidak ada, pakai ZIP mode..."
    curl -L -o agent.zip https://github.com/$AGENT_REPO/archive/refs/heads/main.zip
    unzip -o agent.zip
    mv agent-persistent-main agent-persistent 2>/dev/null || true
  fi
fi
echo "[2/3] Cek python..."
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "python belum ada. Install: sudo apt install python3 python3-pip -y"
  exit 1
fi
echo "[3/3] Jalan 1-klik..."
cd agent-persistent
chmod +x START_AGENT_LINUX.sh 2>/dev/null || true
./START_AGENT_LINUX.sh || bash START_AGENT_LINUX.sh
