import re
import sys
import urllib.parse
from pathlib import Path

# ============================================================
# НАСТРОЙКИ
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

EXTENSIONS = {".txt", ".conf"}
OUTPUT_FILE = BASE_DIR / "generated_links.txt"
AUTHOR_URL = "https://github.com/typ6o6yp"


# ============================================================
# ТЕРМИНАЛ / СТИЛЬ
# ============================================================

class Style:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"

    @staticmethod
    def enable():
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                pass


def c(text, *codes):
    return "".join(codes) + str(text) + Style.RESET


def rule():
    print(c(" ────────────────────────────────────────", Style.GRAY))


def banner():
    print()
    print(
        c(" WireGuard PROTON", Style.BOLD, Style.WHITE)
        + c(" → ", Style.DIM)
        + c("v2rayN", Style.BOLD, Style.CYAN)
    )
    print(c(" генератор ссылок", Style.DIM))
    print()
    rule()
    print()


def info_block(path, count):
    print(c(" папка ", Style.DIM) + c(str(path), Style.WHITE))
    print(c(" файлы ", Style.DIM) + c(".txt · .conf", Style.WHITE))
    print(c(" вывод ", Style.DIM) + c(OUTPUT_FILE.name, Style.WHITE))
    print()
    rule()
    print()
    if count:
        print(c(f" найдено: {count}", Style.CYAN, Style.BOLD))
    else:
        print(c(" профили не найдены", Style.YELLOW))
    print()


def status_ok(name):
    print(c(" ✓ ", Style.GREEN) + c(name, Style.WHITE))


def status_err(name, msg):
    print(c(" ✗ ", Style.RED) + c(name, Style.WHITE))
    print(c(f" {msg}", Style.DIM, Style.RED))


def result_block(total, ok, err):
    print()
    rule()
    print()
    print(c(" результат", Style.BOLD, Style.WHITE))
    print()
    print(c(f" всего {total}", Style.DIM))
    print(c(f" успешно {ok}", Style.GREEN if ok else Style.DIM))
    print(c(f" ошибок {err}", Style.RED if err else Style.DIM))
    print()
    if ok:
        print(c(" файл ", Style.DIM) + c(str(OUTPUT_FILE), Style.CYAN))
    else:
        print(c(" ничего не сохранено", Style.YELLOW))
    print()
    rule()
    print()


def wait_exit():
    """Показывает ссылку автора и ждёт Enter для полного выхода."""
    print(c(f" › {AUTHOR_URL}", Style.BOLD, Style.CYAN))
    print()
    print(c(" Enter", Style.CYAN, Style.BOLD) + c(" — выход", Style.DIM))
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()


# ============================================================
# БУФЕР ОБМЕНА
# ============================================================

def copy_to_clipboard(text):
    """Копирует текст в буфер. Без внешних зависимостей."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        pass

    if sys.platform == "win32":
        try:
            import subprocess
            subprocess.run(
                ["clip"],
                input=text.encode("utf-16le"),
                check=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return True
        except Exception:
            pass

    if sys.platform == "darwin":
        try:
            import subprocess
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        except Exception:
            pass

    try:
        import subprocess
        for cmd in (
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
        ):
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return True
            except Exception:
                continue
    except Exception:
        pass

    return False


# ============================================================
# ИНТЕРАКТИВ: КОПИРОВАНИЕ ССЫЛОК
# ============================================================

def interactive_copy(results):
    """
    results: list[(name, uri)]
    Цикл: выбрать номер → скопировать в буфер → снова или выход.
    При выходе — ссылка автора, затем Enter для закрытия.
    """
    if not results:
        wait_exit()
        return

    while True:
        print(c(" ссылки", Style.BOLD, Style.WHITE))
        print()
        for i, (name, _) in enumerate(results, start=1):
            num = c(f" {i:>2}", Style.CYAN, Style.BOLD)
            print(f"{num} {c(name, Style.WHITE)}")
        print()
        print(
            c(" номер", Style.CYAN, Style.BOLD)
            + c(" — копировать в буфер обмена   ", Style.DIM)
            + c("0", Style.CYAN, Style.BOLD)
            + c(" — выход", Style.DIM)
        )
        print()

        try:
            raw = input(c(" › ", Style.CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if raw in {"", "0", "q", "й", "exit", "выход"}:
            break

        if not raw.isdigit():
            print(c(" введите номер из списка", Style.YELLOW))
            print()
            continue

        idx = int(raw)
        if idx < 1 or idx > len(results):
            print(c(f" нет пункта {idx}", Style.YELLOW))
            print()
            continue

        name, uri = results[idx - 1]
        if copy_to_clipboard(uri):
            print()
            print(c(" ✓ скопировано в буфер обмена  ", Style.GREEN) + c(name, Style.WHITE))
        else:
            print()
            print(c(" ✗ не удалось скопировать", Style.RED))
            print(c(" ссылка ниже — выделите вручную:", Style.DIM))
            print(c(f" {uri}", Style.GRAY))
        print()
        rule()
        print()

    wait_exit()


# ============================================================
# ПАРСЕР WIREGUARD
# ============================================================

def parse_wireguard_config(text):
    data = {}
    multi_keys = {"Address", "AllowedIPs", "DNS"}

    for raw in text.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue

        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key in multi_keys and key in data:
            data[key] = f"{data[key]},{value}"
        else:
            data[key] = value

    return data


def get_profile_name(text, filename):
    match = re.search(r"(?m)^\s*#\s*([^\r\n#]+?)\s*$", text)
    if match:
        candidate = match.group(1).strip()
        if candidate not in {"Interface", "Peer", "PersistentKeepalive"}:
            return candidate

    match = re.search(r"(?im)^\s*#\s*Key\s+for\s+(.+?)\s*$", text)
    if match:
        return match.group(1).strip()

    return filename


def encode(value):
    return urllib.parse.quote(str(value), safe="")


def normalize_address(address):
    if not address:
        return address

    result = []
    for addr in address.split(","):
        addr = addr.strip()
        if not addr:
            continue
        if "/" not in addr:
            addr = f"{addr}/128" if ":" in addr else f"{addr}/32"
        result.append(addr)
    return ",".join(result)


def split_endpoint(endpoint):
    endpoint = endpoint.strip()

    if endpoint.startswith("[") and "]:" in endpoint:
        host, port = endpoint.rsplit("]:", 1)
        return host[1:], port

    if endpoint.count(":") == 1:
        return endpoint.rsplit(":", 1)

    return endpoint, "51820"


# ============================================================
# ГЕНЕРАЦИЯ URI
# ============================================================

def generate_wireguard_uri(data, profile_name):
    private_key = data.get("PrivateKey")
    address = data.get("Address")
    public_key = data.get("PublicKey")
    endpoint = data.get("Endpoint")
    keepalive = data.get("PersistentKeepalive")
    mtu = data.get("MTU")
    psk = data.get("PresharedKey") or data.get("PreSharedKey")
    reserved = data.get("Reserved")

    required = {
        "PrivateKey": private_key,
        "Address": address,
        "PublicKey": public_key,
        "Endpoint": endpoint,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError("нет: " + ", ".join(missing))

    address = normalize_address(address)
    host, port = split_endpoint(endpoint)

    params = [
        f"publickey={encode(public_key)}",
        f"address={encode(address)}",
    ]
    if mtu:
        params.append(f"mtu={encode(mtu)}")
    if keepalive:
        params.append(f"keepalive={encode(keepalive)}")
    if psk:
        params.append(f"presharedkey={encode(psk)}")
    if reserved:
        params.append(f"reserved={encode(reserved)}")

    host_uri = f"[{host}]" if ":" in host and not host.startswith("[") else host

    return (
        f"wireguard://{encode(private_key)}"
        f"@{host_uri}:{port}"
        f"/?{'&'.join(params)}"
        f"#{encode(profile_name)}"
    )


def process_file(file_path):
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = file_path.read_text(encoding="cp1251")
        except Exception as e:
            raise ValueError(f"не удалось прочитать: {e}")

    data = parse_wireguard_config(text)
    name = get_profile_name(text, file_path.stem)
    uri = generate_wireguard_uri(data, name)
    return name, uri


# ============================================================
# MAIN
# ============================================================

def main():
    Style.enable()
    banner()

    files = sorted(
        p for p in BASE_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in EXTENSIONS
        and p.name != OUTPUT_FILE.name
    )

    info_block(BASE_DIR, len(files))

    if not files:
        print(c(" положите .txt / .conf рядом с программой", Style.DIM))
        print()
        wait_exit()
        return

    print(c(" Enter", Style.CYAN, Style.BOLD) + c(" — начать", Style.DIM))
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    print()
    print(c(" обработка…", Style.DIM))
    print()

    results = []
    ok = err = 0

    for path in files:
        try:
            name, uri = process_file(path)
            results.append((name, uri))
            ok += 1
            status_ok(name)
        except Exception as e:
            err += 1
            status_err(path.name, e)

    if results:
        with OUTPUT_FILE.open("w", encoding="utf-8", newline="\n") as f:
            for name, uri in results:
                f.write(f"{name}\n{uri}\n\n")

    result_block(len(files), ok, err)
    interactive_copy(results)


if __name__ == "__main__":
    main()