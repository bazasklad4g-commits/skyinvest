# SkyInvest

Сетка посадочных страниц для зарубежной недвижимости в концепте A.

## Локальный запуск

```bash
npm install
npm run dev
```

Основные страницы:

- `/real-estate` — хаб направлений;
- `/bali-ru`, `/ispania-ru`, `/turkey-ru`, `/dubai` — приоритетные лендинги;
- остальные URL из исходной таблицы собраны в `content/landing-pages.ts`.

## Подключение заявок

Форма отправляет номер на `/api/leads` после первого шага и повторно после выбора страны и бюджета. В Vercel нужно добавить хотя бы один канал:

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GOOGLE_SHEETS_WEBHOOK_URL=
NEXT_PUBLIC_GTM_ID=
NEXT_PUBLIC_SITE_URL=
```

`GOOGLE_SHEETS_WEBHOOK_URL` — URL вебхука Google Apps Script, который записывает JSON-заявки в таблицу. Пока каналы не добавлены, API не сохраняет номер и честно возвращает ошибку.

Контейнер GTM `GTM-WLNZBWMX` подключён в коде как публичное значение по умолчанию. Переменная `NEXT_PUBLIC_GTM_ID` при необходимости его переопределяет.

## Google Ads

Ключи лежат локально в `.secrets/google-ads.yaml`, доступен рабочий аккаунт из комментария `# Рабочий аккаунт:`. Скрипты не добавляются в Vercel и не передают ключи в Git.

```bash
.venv/bin/python scripts/ads_pull.py 30
.venv/bin/python scripts/ads_manage.py list
.venv/bin/python scripts/ads_manage.py status --campaign-id ID --set PAUSED --apply
.venv/bin/python scripts/ads_manage.py budget --budget-id ID --daily 50 --apply
```

Без `--apply` команды изменения только показывают предполагаемое действие.

Исследование находится в `docs/RESEARCH.md`, техническое задание — в `docs/TECHNICAL-SPEC.md`.
