#!/usr/bin/env bash

set -euo pipefail

APP_DIR="${SERVER_CONTEXT_SCANNER_HOME:-$HOME/server-context-scanner}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_FILE="$HOME/.bashrc"

mkdir -p "$APP_DIR/reports"

if [ "$SOURCE_DIR" != "$APP_DIR" ]; then
  cp "$SOURCE_DIR/scan_server_context.sh" "$APP_DIR/scan_server_context.sh"
  [ -f "$SOURCE_DIR/README.md" ] && cp "$SOURCE_DIR/README.md" "$APP_DIR/README.md"
  [ -f "$SOURCE_DIR/ai_prompt_template.md" ] && cp "$SOURCE_DIR/ai_prompt_template.md" "$APP_DIR/ai_prompt_template.md"
fi

chmod +x "$APP_DIR/scan_server_context.sh"

touch "$PROFILE_FILE"

sed -i '/^alias scan-server=/d' "$PROFILE_FILE"

TMP_PROFILE="$(mktemp)"
awk '
  $0 == "# Begin Server Context Scanner" || $0 == "# Server Context Scanner" {
    in_block = 1
    buffer = $0 ORS
    next
  }
  in_block {
    buffer = buffer $0 ORS
    if ($0 == "# End Server Context Scanner") {
      in_block = 0
      buffer = ""
    }
    next
  }
  { print }
  END {
    if (in_block) {
      printf "%s", buffer
    }
  }
' "$PROFILE_FILE" > "$TMP_PROFILE"
mv "$TMP_PROFILE" "$PROFILE_FILE"

{
  echo ""
  echo "# Begin Server Context Scanner"
  echo "scan-server() {"
  echo "  case \"\${1:-}\" in"
  echo "    --help|-h)"
  echo "      \"$APP_DIR/scan_server_context.sh\" \"\$@\""
  echo "      ;;"
  echo "    *)"
  echo "      \"$APP_DIR/scan_server_context.sh\" \"\$@\" && cat \"$APP_DIR/reports/server_context_latest.md\""
  echo "      ;;"
  echo "  esac"
  echo "}"
  echo "# End Server Context Scanner"
} >> "$PROFILE_FILE"

echo "Installed scan-server function to $PROFILE_FILE"

echo ""
echo "Installed Server Context Scanner to:"
echo "$APP_DIR"
echo ""
echo "To activate the function in the current shell, run:"
echo "source $PROFILE_FILE"
echo ""
echo "Then scan the server with:"
echo "scan-server"
echo ""
echo "For a detailed diagnostic report, run:"
echo "scan-server --full"
