#!/usr/bin/env python3
"""Launch MoneyPrinterTurbo with keys pulled from the DansLab secret resolver.

MoneyPrinterTurbo only reads credentials from config.toml. The fleet keeps its
credentials in the macOS Keychain (mac-studio), the Windows user environment,
or ~/.openclaw/fleet.env — never in files under version control.

This launcher bridges the two: it resolves each key at startup and writes it
into config.toml just before handing off to Streamlit. Values are never printed
and config.toml stays gitignored.

Usage:
    python launch_with_secrets.py           # start the WebUI
    python launch_with_secrets.py --check   # report which keys resolve, no launch
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# This machine's TLS is intercepted, so certifi's bundle lacks the issuer.
# truststore routes verification through the Windows certificate store.
import truststore

truststore.inject_into_ssl()

HERE = Path(__file__).resolve().parent
RESOLVER_DIR = (
    HERE.parent / "Youtube-videos" / "danslab-100k-2027-v6"
    / "Module 1 - Step 1" / "dashboard"
)

sys.path.insert(0, str(RESOLVER_DIR))
try:
    from engines._secrets import resolve, status_snapshot
except ImportError:
    sys.exit(f"Cannot import the secret resolver from {RESOLVER_DIR}")

import toml

CONFIG = HERE / "config.toml"

# config.toml key -> env var names to try, in order.
# List-valued config fields (the *_api_keys rotation lists) are marked as_list.
MAPPING = {
    "pexels_api_keys":  (["PEXELS_API_KEY"], True),
    "pixabay_api_keys": (["PIXABAY_API_KEY"], True),
    # The fleet routes LLM traffic through OpenRouter, which speaks the OpenAI
    # Chat Completions protocol, so it fills MoneyPrinterTurbo's "openai" slot.
    "openai_api_key":   (["OPENROUTER_API_KEY"], False),
    "gemini_api_key":   (["GEMINI_API_KEY"], False),
    "moonshot_api_key": (["MOONSHOT_API_KEY", "KIMI_MOONSHOT_API_KEY"], False),
}

# Fixed values that must accompany the OpenRouter key.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "deepseek/deepseek-v3.2-exp"


def check() -> None:
    names = [n for names, _ in MAPPING.values() for n in names]
    for name, info in status_snapshot(names).items():
        if info["configured"]:
            print(f"  OK      {name:24s} from {info['source']} (len {info['len']})")
        else:
            print(f"  MISSING {name:24s}")


def inject() -> list[str]:
    doc = toml.loads(CONFIG.read_text(encoding="utf-8"))
    app = doc["app"]
    filled = []
    for cfg_key, (env_names, as_list) in MAPPING.items():
        value = resolve(*env_names)
        if not value:
            continue
        app[cfg_key] = [value] if as_list else value
        filled.append(cfg_key)
    if app.get("openai_api_key"):
        app["openai_base_url"] = OPENROUTER_BASE_URL
        app["openai_model_name"] = OPENROUTER_MODEL
    CONFIG.write_text(toml.dumps(doc), encoding="utf-8")
    return filled


def main() -> None:
    if not CONFIG.exists():
        sys.exit("config.toml missing — copy it from config.example.toml first.")

    if "--check" in sys.argv:
        check()
        return

    filled = inject()
    print(f"Injected into config.toml: {', '.join(filled) or 'nothing resolved'}")

    # ElevenLabs voice, if the fleet has a key for it.
    elevenlabs = resolve("ELEVENLABS_API_KEY")
    if elevenlabs:
        doc = toml.loads(CONFIG.read_text(encoding="utf-8"))
        doc["elevenlabs"]["api_key"] = elevenlabs
        CONFIG.write_text(toml.dumps(doc), encoding="utf-8")
        print("Injected into config.toml: elevenlabs.api_key")

    os.environ["PYTHONPATH"] = str(HERE)
    os.execv(
        sys.executable,
        [
            sys.executable, "-m", "streamlit", "run", str(HERE / "webui" / "Main.py"),
            "--server.address=127.0.0.1", "--server.port=8501",
            "--browser.gatherUsageStats=False", "--server.headless=True",
        ],
    )


if __name__ == "__main__":
    main()
