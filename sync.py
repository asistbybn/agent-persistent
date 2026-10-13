"""
SYNC.PY - Otak Auto-Upload / Auto-Download
Hanya sync: brain/, skills/, tools/, memory.jsonl, *.py inti
Tidak sync: log, __pycache__, /tmp, checkpoint lokal besar

Cara pakai:
  python sync.py push   -> upload setelah pemakaian
  python sync.py pull   -> download di komputer baru
  python sync.py status -> lihat versi lokal vs remote
"""
import os, json, zipfile, datetime, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).parent
MANIFEST = ROOT / "agent_manifest.json"

# Folder/file yang BOLEH ikut (sesuai permintaan user)
ALLOW_DIRS = ["brain", "skills", "tools"]
ALLOW_FILES = [
    "memory.jsonl",
    "memory_store.py",
    "persistent_agent.py",
    "main_agent.py",
    "requirements.txt",
    "agent_manifest.json",
    "sync.py",
]

def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"version": 0, "updated_at": "", "history": []}

def save_manifest(version, note="auto"):
    data = load_manifest()
    data["version"] = version
    data["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    data["history"].append({"v": version, "at": data["updated_at"], "note": note})
    data["history"] = data["history"][-50:]
    MANIFEST.write_text(json.dumps(data, indent=2))
    return data

def collect_files():
    files = []
    for d in ALLOW_DIRS:
        p = ROOT / d
        p.mkdir(exist_ok=True)
        for f in p.rglob("*"):
            if f.is_file() and "__pycache__" not in str(f) and f.suffix not in [".log", ".tmp"]:
                files.append(f)
    for name in ALLOW_FILES:
        p = ROOT / name
        if p.exists():
            files.append(p)
    return files

def make_bundle(out_path):
    files = collect_files()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(ROOT))
    print(f"bundle: {out_path} ({len(files)} file)")
    return out_path

def do_push(note="auto-upload setelah pakai"):
    m = load_manifest()
    v = m.get("version", 0) + 1
    bundle = ROOT / f"agent-brain-v{v}.zip"
    make_bundle(bundle)

    # 1) Coba GCS jika ada bucket
    bucket = os.environ.get("GCS_BUCKET", "")
    if bucket:
        try:
            from google.cloud import storage
            client = storage.Client()
            b = client.bucket(bucket.replace("gs://", ""))
            b.blob(f"agent-brain-v{v}.zip").upload_from_filename(str(bundle))
            b.blob("agent-brain-latest.zip").upload_from_filename(str(bundle))
            print(f"uploaded ke {bucket}")
        except Exception as e:
            print(f"GCS gagal: {e} -> lanjut ke git")

    # 2) Coba git push (tanpa login tambahan jika sudah pakai SSH/credential helper)
    try:
        import subprocess
        subprocess.run(["git", "add", *ALLOW_DIRS, *ALLOW_FILES], cwd=ROOT, check=False)
        subprocess.run(["git", "commit", "-m", f"brain v{v} {note}"], cwd=ROOT, check=False)
        subprocess.run(["git", "push"], cwd=ROOT, check=False)
        print("git push dicoba")
    except Exception as e:
        print(f"git gagal: {e}")

    save_manifest(v, note)
    print(f"push selesai -> v{v}")
    return v

def do_pull():
    # 1) Coba GCS latest
    bucket = os.environ.get("GCS_BUCKET", "")
    if bucket:
        try:
            from google.cloud import storage
            client = storage.Client()
            b = client.bucket(bucket.replace("gs://", ""))
            latest = ROOT / "agent-brain-latest.zip"
            b.blob("agent-brain-latest.zip").download_to_filename(str(latest))
            print(f"download dari {bucket}")
            with zipfile.ZipFile(latest) as z:
                z.extractall(ROOT)
            print("pull dari GCS selesai")
            return True
        except Exception as e:
            print(f"GCS pull gagal: {e} -> coba git")

    # 2) Coba git pull
    try:
        import subprocess
        r = subprocess.run(["git", "pull"], cwd=ROOT, capture_output=True, text=True)
        print(r.stdout or r.stderr or "git pull selesai")
        return True
    except Exception as e:
        print(f"pull gagal: {e}")
        return False

def do_status():
    m = load_manifest()
    files = collect_files()
    print(f"version lokal: v{m.get('version',0)}")
    print(f"updated: {m.get('updated_at','-')}")
    print(f"file ter-track: {len(files)}")
    for d in ALLOW_DIRS:
        n = len(list((ROOT/d).rglob('*')) ) if (ROOT/d).exists() else 0
        print(f"  - {d}/ : {n} file")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "push":
        note = " ".join(sys.argv[2:]) or "auto-upload setelah pakai"
        do_push(note)
    elif cmd == "pull":
        do_pull()
    else:
        do_status()
