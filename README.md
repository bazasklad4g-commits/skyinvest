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

Исследование находится в `docs/RESEARCH.md`, техническое задание — в `docs/TECHNICAL-SPEC.md`.
