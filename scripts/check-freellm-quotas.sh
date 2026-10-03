#!/bin/bash
set -euo pipefail
# HERMES_HOME — реальный .env (DEC-047)
source /mnt/ai-ssd/hermes/.env
curl -s http://127.0.0.1:3001/v1/quota-forecast \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    forecasts = data.get('forecasts', [])
    alerts = []
    for provider in forecasts:
        if provider.get('low_balance'):
            alerts.append(f'⚠️ {provider[\"name\"]}: {provider[\"remaining\"]} осталось')
    if alerts:
        print('\n'.join(alerts))
    else:
        print('✅ Все квоты в норме')
except Exception as e:
    print(f'⚠️ Ошибка: {e}')
"
