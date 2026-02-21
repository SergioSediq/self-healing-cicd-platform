"""Pre-apply verification: run tests/checks before applying fix."""
import os
import subprocess
from pathlib import Path


def run_pre_verify(file_path: str, project_root: Path | None = None) -> tuple[bool, str]:
    """
    Run quick verification before applying fix.
    Returns (passed, message).
    """
    root = project_root or Path(".")
    if os.getenv("SKIP_PRE_VERIFY", "").lower() in ("1", "true", "yes"):
        return True, "Skipped"

    # Lint/syntax check based on file type
    ext = Path(file_path).suffix.lower()
    if ext in (".js", ".ts", ".jsx", ".tsx"):
        try:
            r = subprocess.run(
                ["node", "--check", str(root / file_path)] if ext == ".js" else ["npx", "tsc", "--noEmit"],
                capture_output=True,
                text=True,
                cwd=root,
                timeout=30,
            )
            if r.returncode != 0:
                return False, r.stderr or r.stdout or "Check failed"
        except FileNotFoundError:
            pass  # node/npx not found, skip
        except subprocess.TimeoutExpired:
            return False, "Verification timeout"
    elif ext == ".py":
        try:
            r = subprocess.run(
                ["python", "-m", "py_compile", str(root / file_path)],
                capture_output=True,
                text=True,
                cwd=root,
                timeout=10,
            )
            if r.returncode != 0:
                return False, r.stderr or "Syntax error"
        except FileNotFoundError:
            pass
    return True, "OK"
