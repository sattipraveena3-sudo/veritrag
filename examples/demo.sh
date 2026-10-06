#!/usr/bin/env bash
set -euo pipefail

veritrag ingest examples/company_policy.txt --source-id acme-policy --title "Acme Cloud Policy"
veritrag search "Enterprise priority-one response time" --top-k 3
veritrag audit \
  --question "What response time does Enterprise support target for priority-one incidents?" \
  --answer "Enterprise support targets a one-hour response time for priority-one incidents." \
  --fail-on-risk
