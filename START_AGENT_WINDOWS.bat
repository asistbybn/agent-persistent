@echo off
REM START_AGENT_WINDOWS.bat - 1x KLIK langsung jalan (device umum / warnet)
REM Yang kamu lakukan: klik 2x -> tempel MEMORY_URL + MEMORY_KEY -> Enter
REM Sisanya AUTO: pull -> jalan -> push tiap step

echo.
echo ================================
echo  AI AGENT 1-KLIK (Windows)
echo ================================
echo.

cd /d %~dp0

where python >nul 2>nul
if %errorlevel% neq 0 (
  echo Python belum ada. Install dulu dari https://python.org/downloads/
  pause
  exit /b
)

echo [AUTO] cek kebutuhan...
pip install -q -r requirements.txt 2>nul

echo [AUTO] download otak terbaru...
python sync.py pull 2>nul

echo.
echo [JALAN] tinggal tempel API key 1x...
python mulai.py

echo.
echo Selesai - otak sudah auto-upload ke cloud
pause
