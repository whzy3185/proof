"""Internal helper for compiling/running the exact C++ finite verifier."""
from pathlib import Path
import os, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "exact_box_core.cpp"
BUILD = ROOT / ".build"
BIN = BUILD / "exact_box_core"

def executable():
    BUILD.mkdir(exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("clang++")
    if compiler is None:
        raise SystemExit("A C++17 compiler (g++ or clang++) is required for the full finite checks.")
    if not BIN.exists() or BIN.stat().st_mtime < SRC.stat().st_mtime:
        subprocess.run([compiler, "-O3", "-std=c++17", "-Wall", "-Wextra", str(SRC), "-o", str(BIN)], check=True)
    return BIN
