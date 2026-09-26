# Персонализация системы

После клонирования репозитория замените следующие placeholders на ваши реальные значения:

## Обязательные замены

### `.env` файл
```bash
# Telegram
TELEGRAM_BOT_TOKEN=<получить у @BotFather>
TELEGRAM_CHAT_ID=<ваш Telegram user ID>
TELEGRAM_ALLOWED_USERS=<ваш Telegram user ID>

# GitHub
GITHUB_USER=<ваш GitHub username>
GITHUB_TOKEN=<GitHub fine-grained token>
GITHUB_REPO=<имя вашего репозитория>

# API ключи
OPENAI_API_KEY=<ваш OpenAI API key>
NVIDIA_API_KEY=<ваш NVIDIA API key>

# Supabase (если используете)
SUPABASE_URL=<ваш Supabase project URL>
SUPABASE_SERVICE_ROLE_KEY=<ваш service role key>
SUPABASE_ANON_KEY=<ваш anon key>

# AWS/R2 (если используете)
AWS_ACCESS_KEY_ID=<ваш AWS access key>
AWS_SECRET_ACCESS_KEY=<ваш AWS secret key>
R2_ENDPOINT=<ваш R2 endpoint>
```

### Получение Telegram Chat ID
1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Скопируйте ваш `Id` (число)

### Получение GitHub Token
1. Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Создать токен с правами `Contents: Read and write` для вашего репозитория

### Получение API ключей
- **OpenAI**: https://platform.openai.com/api-keys
- **NVIDIA NIM**: https://build.nvidia.com/
- **Supabase**: Project Settings → API

## Проверка после персонализации

```bash
# Проверить что все переменные заполнены
grep -E "=<" ~/ai-system/.env && echo "⚠️ Есть незаполненные переменные" || echo "✅ Все переменные заполнены"

# Тест Telegram
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq -r '.result.username'

# Тест GitHub
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | jq -r '.login'
```
