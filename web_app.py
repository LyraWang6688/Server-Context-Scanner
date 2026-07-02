#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, TypeAlias

from flask import Flask, Response, jsonify, render_template, request, send_file


APP_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = APP_DIR / "scan_server_context.sh"
REPORT_PATH = APP_DIR / "reports" / "server_context_latest.md"
SCAN_TIMEOUT_SECONDS = int(os.environ.get("SERVER_CONTEXT_SCAN_TIMEOUT", "120"))
WEB_TOKEN = os.environ.get("SERVER_CONTEXT_WEB_TOKEN", "").strip()
SCAN_LOCK = threading.Lock()
AuthResult: TypeAlias = tuple[bool, Response | tuple[Response, int] | None]

app = Flask(
    __name__,
    template_folder=str(APP_DIR / "web" / "templates"),
    static_folder=str(APP_DIR / "web" / "static"),
)


def require_token_if_configured() -> AuthResult:
    if not WEB_TOKEN:
        return True, None

    supplied = request.headers.get("X-Scanner-Token", "")
    if supplied == WEB_TOKEN:
        return True, None

    return False, (jsonify({"ok": False, "error": "Unauthorized"}), 401)


def read_latest_report() -> str:
    if not REPORT_PATH.exists():
        return ""
    return REPORT_PATH.read_text(encoding="utf-8", errors="replace")


def report_payload(mode: str, report: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "mode": mode,
        "report": report,
        "reportPath": str(REPORT_PATH),
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "lineCount": len(report.splitlines()),
        "charCount": len(report),
    }
    if extra:
        payload.update(extra)
    return payload


@app.get("/")
def index() -> str:
    return render_template("index.html", token_required=bool(WEB_TOKEN))


@app.get("/healthz")
def healthz() -> Response:
    return jsonify({"ok": True, "service": "server-context-scanner-web"})


@app.get("/api/latest")
def latest() -> Response:
    ok, error_response = require_token_if_configured()
    if not ok:
        return error_response  # type: ignore[return-value]

    report = read_latest_report()
    if not report:
        return jsonify({"ok": False, "error": "No report has been generated yet."}), 404
    return jsonify(report_payload("latest", report))


@app.post("/api/scan")
def scan() -> Response:
    ok, error_response = require_token_if_configured()
    if not ok:
        return error_response  # type: ignore[return-value]

    body = request.get_json(silent=True) or {}
    mode = body.get("mode", "summary")
    if mode not in {"summary", "full"}:
        return jsonify({"ok": False, "error": "Invalid mode. Use summary or full."}), 400

    if not SCRIPT_PATH.exists():
        return jsonify({"ok": False, "error": f"Scanner script not found: {SCRIPT_PATH}"}), 500

    command = [str(SCRIPT_PATH)]
    if mode == "full":
        command.append("--full")

    with SCAN_LOCK:
        try:
            result = subprocess.run(
                command,
                cwd=str(APP_DIR),
                capture_output=True,
                text=True,
                timeout=SCAN_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return jsonify({"ok": False, "error": f"Scan timed out after {SCAN_TIMEOUT_SECONDS}s."}), 504

        report = read_latest_report()
    if result.returncode != 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Scanner script failed.",
                    "returnCode": result.returncode,
                    "stdout": result.stdout[-4000:],
                    "stderr": result.stderr[-4000:],
                    "report": report,
                }
            ),
            500,
        )

    return jsonify(
        report_payload(
            mode,
            report,
            {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            },
        )
    )


@app.get("/download/latest")
def download_latest() -> Response:
    ok, error_response = require_token_if_configured()
    if not ok:
        return error_response  # type: ignore[return-value]

    if not REPORT_PATH.exists():
        return jsonify({"ok": False, "error": "No report has been generated yet."}), 404
    return send_file(
        REPORT_PATH,
        mimetype="text/markdown; charset=utf-8",
        as_attachment=True,
        download_name=REPORT_PATH.name,
    )


if __name__ == "__main__":
    host = os.environ.get("SERVER_CONTEXT_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("SERVER_CONTEXT_WEB_PORT", "8765"))
    if host in {"0.0.0.0", "::"} and not WEB_TOKEN:
        print(
            "WARNING: Server Context Scanner Web UI is binding to a public interface "
            "without SERVER_CONTEXT_WEB_TOKEN. Use Nginx Basic Auth or set a strong token "
            "before exposing this service.",
            file=sys.stderr,
        )
    app.run(host=host, port=port)
