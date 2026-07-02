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

ALIAS_LINE="alias scan-server='$APP_DIR/scan_server_context.sh && cat $APP_DIR/reports/server_context_latest.md'"

touch "$PROFILE_FILE"

if grep -Fq "alias scan-server=" "$PROFILE_FILE"; then
  echo "scan-server alias already exists in $PROFILE_FILE"
else
  {
    echo ""
    echo "# Server Context Scanner"
    echo "$ALIAS_LINE"
  } >> "$PROFILE_FILE"
  echo "Added scan-server alias to $PROFILE_FILE"
fi

echo ""
echo "Installed Server Context Scanner to:"
echo "$APP_DIR"
echo ""
echo "To activate the alias in the current shell, run:"
echo "source $PROFILE_FILE"
echo ""
echo "Then scan the server with:"
echo "scan-server"
