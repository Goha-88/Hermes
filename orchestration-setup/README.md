# Hermes Orchestration Setup (Goha-88)

Персональная настройка Hermes Agent («Карина»): оркестрация моделей, навыки и скрипты.
Версионируемый бэкап — **без секретов и без личных данных idocs**.

## Что внутри
- `config.yaml` — конфиг Hermes (реальные токены замаскированы плейсхолдерами `<...>`).
- `SOUL.md` — операционные конвенции + карта маршрутизации задач по моделям.
- `skills/` — навыки оркестрации (image-gen, video-gen, data-analysis, documents, brand-voice, hermes-playbook, find-skills) + 31 Firecrawl-навык.
- `bin/` — CLI: `hermes-spend` (учёт трат), `hermes-image` / `-pro` / `-brand` (картинки), `hermes-video` / `-kling` (видео).
- `hooks/spend-audit/` — gateway-хук поштучного учёта трат.
- `.env.example` — шаблон переменных окружения.

## Оркестрация
**Лейны (переключатели модели):** `/chat /strategy /research /sales /content /code /review /reviewlite /data /docs /agentic`

**Картинки:** FLUX 1.1 Pro Ultra (фото) · Recraft V3 (бренд/лого) · gemini (быстро)
**Видео:** Veo 3.1 (премиум+звук) · Kling 2.5 (дёшево/быстро)
**Провайдеры:** OpenRouter · DeepSeek · Perplexity · ElevenLabs · Replicate · MCP: GitHub/Firecrawl/Miro

## Восстановление / откат
1. `git clone` репозиторий.
2. Скопировать `config.yaml`, `SOUL.md`, `skills/`, `hooks/` → `~/.hermes/`.
3. Скопировать `bin/*` → `~/.local/bin/` и `chmod +x`.
4. `cp .env.example ~/.hermes/.env`, вписать реальные ключи.
5. В `config.yaml` заменить плейсхолдеры `<...>` на реальные токены.
6. `hermes gateway restart`.

## ⚠️ Безопасность
Реальные ключи здесь НЕ хранятся (только локально в `~/.hermes/.env` и `config.yaml`).
Бизнес-память idocs (стратегия/MRR/команда) и персона намеренно исключены.
