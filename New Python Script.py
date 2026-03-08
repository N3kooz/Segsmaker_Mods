import os
import sys
from pathlib import Path

# ─────────────────────────────────────────
#  Warna terminal
# ─────────────────────────────────────────
R  = "\033[91m"   # merah
G  = "\033[92m"   # hijau
Y  = "\033[93m"   # kuning
B  = "\033[94m"   # biru
C  = "\033[96m"   # cyan
W  = "\033[97m"   # putih
DIM = "\033[2m"   # redup
RESET = "\033[0m"

# ─────────────────────────────────────────
#  File yang di-skip (binary / tidak perlu)
# ─────────────────────────────────────────
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mkv",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".bin", ".so", ".dll", ".dylib",
    ".pyc", ".pyo", ".pyd",
    ".safetensors", ".ckpt", ".pt", ".pth",
    ".ttf", ".otf", ".woff", ".woff2",
    ".pdf", ".docx", ".xlsx",
}

SKIP_DIRS = {
    "__pycache__", ".git", ".svn", "node_modules",
    ".venv", "venv", "env", ".env",
    ".idea", ".vscode",
}


def is_readable(path: Path) -> bool:
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return False
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            f.read(512)
        return True
    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
        return False


def scan_files(root: Path) -> list[Path]:
    """Kumpulkan semua file yang bisa dibaca secara rekursif."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Hapus folder yang di-skip dari traversal
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fp = Path(dirpath) / fname
            if is_readable(fp):
                found.append(fp)
    return sorted(found)


def search_in_file(path: Path, keyword: str) -> list[tuple[int, str]]:
    """Kembalikan list (nomor_baris, isi_baris) yang mengandung keyword."""
    hits = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines, 1):
            if keyword in line:
                hits.append((i, line))
    except Exception:
        pass
    return hits


def replace_in_file(path: Path, old: str, new: str) -> int:
    """Ganti semua kemunculan old → new di file, kembalikan jumlah penggantian."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        count = content.count(old)
        if count:
            path.write_text(content.replace(old, new), encoding="utf-8")
        return count
    except Exception as e:
        print(f"{R}  ERROR saat menulis {path}: {e}{RESET}")
        return 0


def print_banner():
    print(f"""
{C}╔══════════════════════════════════════════════════════╗
║          🔍  TEXT FINDER & REPLACER  🔍              ║
║          Script by segsmaker project                 ║
╚══════════════════════════════════════════════════════╝{RESET}
""")


def get_project_root() -> Path:
    """Root project = folder tempat replace.py ini berada."""
    return Path(__file__).parent.resolve()


def main():
    print_banner()

    root = get_project_root()
    print(f"{B}📁 Root project : {W}{root}{RESET}\n")

    # ── Input teks yang dicari ──
    print(f"{Y}Masukkan teks / link yang ingin dicari:{RESET}")
    keyword = input(f"{C}  🔎 Cari  : {W}").strip()
    if not keyword:
        print(f"{R}Teks tidak boleh kosong. Keluar.{RESET}")
        sys.exit(1)

    # ── Scan semua file ──
    print(f"\n{DIM}Memindai file...{RESET}")
    all_files = scan_files(root)
    print(f"{G}  ✔ Total file terbaca : {len(all_files)}{RESET}\n")

    # ── Cari keyword ──
    results: dict[Path, list[tuple[int, str]]] = {}
    for fp in all_files:
        hits = search_in_file(fp, keyword)
        if hits:
            results[fp] = hits

    if not results:
        print(f"{Y}⚠  Teks '{keyword}' tidak ditemukan di file manapun.{RESET}")
        sys.exit(0)

    # ── Tampilkan hasil ──
    total_hits = sum(len(v) for v in results.values())
    print(f"{G}✔ Ditemukan {total_hits} kemunculan di {len(results)} file:{RESET}\n")

    for fp, hits in results.items():
        rel = fp.relative_to(root)
        print(f"  {B}📄 {rel}{RESET}")
        for lineno, line in hits:
            highlighted = line.replace(keyword, f"{R}{keyword}{G}")
            print(f"     {DIM}baris {lineno:>4} :{RESET} {G}{highlighted}{RESET}")
        print()

    # ── Konfirmasi replace ──
    print(f"{Y}Apakah ingin mengganti teks di atas? (y/n){RESET}")
    confirm = input(f"{C}  → {W}").strip().lower()
    if confirm != "y":
        print(f"\n{Y}Dibatalkan. Tidak ada file yang diubah.{RESET}")
        sys.exit(0)

    # ── Input teks pengganti ──
    print(f"\n{Y}Masukkan teks / link pengganti:{RESET}")
    replacement = input(f"{C}  ✏  Ganti : {W}").strip()

    # ── Preview sebelum eksekusi ──
    print(f"\n{Y}Preview perubahan:{RESET}")
    print(f"  {R}Lama : {keyword}{RESET}")
    print(f"  {G}Baru : {replacement}{RESET}")
    print(f"\n{Y}Lanjutkan replace di {len(results)} file? (y/n){RESET}")
    final = input(f"{C}  → {W}").strip().lower()
    if final != "y":
        print(f"\n{Y}Dibatalkan. Tidak ada file yang diubah.{RESET}")
        sys.exit(0)

    # ── Eksekusi replace ──
    print()
    total_replaced = 0
    for fp, _ in results.items():
        rel = fp.relative_to(root)
        count = replace_in_file(fp, keyword, replacement)
        total_replaced += count
        print(f"  {G}✔ {rel}  ({count} penggantian){RESET}")

    print(f"\n{G}✅ Selesai! Total {total_replaced} penggantian di {len(results)} file.{RESET}\n")


if __name__ == "__main__":
    main()
