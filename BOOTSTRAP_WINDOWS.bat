@echo off
REM BOOTSTRAP_WINDOWS.bat - FILE KECIL untuk dibawa di HP / Flashdisk / Catatan
REM Fungsi: download semua file agent dari GitHub, lalu jalan 1-klik + API key
REM Cara pakai di PC BARU / warnet:
REM   1. Copy file ini saja (2 KB) atau ketik 1 baris di bawah di CMD
REM   2. Klik 2x -> tempel MEMORY_URL + MEMORY_KEY -> Enter
REM   3. Selesai, sisanya AUTO

echo.
echo ================================
echo  AMBIL AGENT DARI CLOUD
echo ================================
echo.

REM ==== SUDAH DI-SET ke asistbybn ====
if "%AGENT_REPO%"=="" set AGENT_REPO=asistbybn/agent-persistent

echo [1/3] Download dari github.com/%AGENT_REPO% ...
if exist agent-persistent (
  cd agent-persistent
  git pull 2>nul
  cd ..
) else (
  where git >nul 2>nul
  if %errorlevel%==0 (
    git clone https://github.com/%AGENT_REPO%.git
  ) else (
    echo git tidak ada, pakai ZIP mode...
    curl -L -o agent.zip https://github.com/%AGENT_REPO%/archive/refs/heads/main.zip
    tar -xf agent.zip
    if exist agent-persistent-main ren agent-persistent-main agent-persistent
  )
)

echo [2/3] Cek python...
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo Python belum ada. Install: https://python.org/downloads/
  pause
  exit /b
)

echo [3/3] Jalan 1-klik...
cd agent-persistent
call START_AGENT_WINDOWS.bat
