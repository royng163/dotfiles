#!/bin/bash
# Minimal Claude Code status line
# Displays: model name and 5-hour session limit

input=$(cat)

model_name=$(echo "$input" | jq -r '.model.display_name // empty')
five_hour_limit=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')

# Build compact status line
parts=""

if [ -n "$model_name" ]; then
  parts="$model_name"
fi

if [ -n "$five_hour_limit" ]; then
  if [ -n "$parts" ]; then
    parts="$parts | "
  fi
  parts="${parts}5h:$(printf '%.0f' "$five_hour_limit")%"
fi

printf '%s\n' "$parts"
