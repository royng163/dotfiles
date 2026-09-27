#!/bin/bash
# Claude Code status line: model + effort, context tokens, 5h/7d limits, git worktree

input=$(cat)

IFS=$'\t' read -r model effort ctx five seven worktree < <(echo "$input" | jq -r '[
  .model.display_name // "",
  .effort.level // "",
  .context_window.total_input_tokens // "",
  .rate_limits.five_hour.used_percentage // "",
  .rate_limits.seven_day.used_percentage // "",
  .workspace.git_worktree // ""
] | map(tostring | if . == "" then "-" else . end) | @tsv')

parts=()
head="${model#-}"
[ "$effort" != "-" ] && head="$head $effort"
[ -n "$head" ] && parts+=("$head")
[ "$ctx" != "-" ] && [ "$ctx" != "0" ] && parts+=("ctx $((ctx / 1000))k")

limits=""
[ "$five" != "-" ] && limits="5h:$(printf '%.0f' "$five")%"
[ "$seven" != "-" ] && limits="${limits:+$limits }7d:$(printf '%.0f' "$seven")%"
[ -n "$limits" ] && parts+=("$limits")

[ "$worktree" != "-" ] && parts+=("$worktree")

out=""
for p in "${parts[@]}"; do out="${out:+$out | }$p"; done
printf '%s\n' "$out"
