# Пример: оргструктура на 63 элемента

Полный DSL из сессии с Гохой — 1 оркестратор + 5 департаментов × 10 агентов.

## Исходные данные

- Frame: 3200×1800, тёмный фон (#0F172A)
- 5 колонок департаментов с подколонками по 2
- 5 стрелок от оркестратора к департаментам
- 50 агентов (shapes) + 5 департаментов + 1 оркестратор + 1 итоговый блок = 57 shapes
- 5 connectors
- 1 frame
- Всего: 63 элемента

## Координаты

| Элемент | x | y | w | h |
|---|---|---|---|---|
| Оркестратор | 1600 | 80 | 440 | 90 |
| Департаменты | 280/900/1520/2140/2760 | 280 | 460 | 70 |
| Агенты (лев. колонка) | деп_x | 420-660 шаг 60 | 200 | 50 |
| Агенты (прав. колонка) | деп_x+260 | 420-660 шаг 60 | 200 | 50 |
| Итоговый блок | 1600 | 800 | 500 | 60 |

## DSL

```
# === ОСНОВНОЙ FRAME ===
org FRAME x=0 y=-200 w=3200 h=1800 fill=#0F172A "НЕЙРО-ОРГСТРУКТУРА IDOCS"

# === ОРКЕСТРАТОР ===
orch SHAPE parent=org x=1600 y=80 w=440 h=90 type=round_rectangle fill=#7C3AED fill_opacity=1.0 color=#FFFFFF font=plex_sans size=22 valign=middle border_color=#A78BFA border_width=3 "<p>🎯 ГЛАВНЫЙ ОРКЕСТРАТОР</p>"

# === СТРЕЛКИ ===
c1 CONNECTOR from=orch to=des shape=elbowed stroke_color=#7C3AED end_cap=stealth
c2 CONNECTOR from=orch to=mar shape=elbowed stroke_color=#2563EB end_cap=stealth
c3 CONNECTOR from=orch to=sal shape=elbowed stroke_color=#059669 end_cap=stealth
c4 CONNECTOR from=orch to=dev shape=elbowed stroke_color=#EA580C end_cap=stealth
c5 CONNECTOR from=orch to=cs shape=elbowed stroke_color=#DC2626 end_cap=stealth

# === ДЕПАРТАМЕНТЫ ===
des SHAPE parent=org x=280 y=280 w=460 h=70 type=round_rectangle fill=#7C3AED color=#FFFFFF font=plex_sans size=18 valign=middle "<p>🎨 ДИЗАЙН</p>"
mar SHAPE parent=org x=900 y=280 w=460 h=70 type=round_rectangle fill=#2563EB color=#FFFFFF font=plex_sans size=18 valign=middle "<p>📢 МАРКЕТИНГ</p>"
sal SHAPE parent=org x=1520 y=280 w=460 h=70 type=round_rectangle fill=#059669 color=#FFFFFF font=plex_sans size=18 valign=middle "<p>💰 ПРОДАЖИ</p>"
dev SHAPE parent=org x=2140 y=280 w=460 h=70 type=round_rectangle fill=#EA580C color=#FFFFFF font=plex_sans size=18 valign=middle "<p>⚙️ РАЗРАБОТКА</p>"
cs SHAPE parent=org x=2760 y=280 w=460 h=70 type=round_rectangle fill=#DC2626 color=#FFFFFF font=plex_sans size=18 valign=middle "<p>🤝 КЛИЕНТСКИЙ СЕРВИС</p>"

# === АГЕНТЫ (пример: дизайн) ===
d1 SHAPE parent=org x=280 y=420 w=200 h=50 type=rectangle fill=#EDE9FE color=#4C1D95 font=roboto size=10 valign=middle border_color=#C4B5FD "Арт-директор"
d2 SHAPE parent=org x=280 y=480 w=200 h=50 type=rectangle fill=#EDE9FE color=#4C1D95 font=roboto size=10 valign=middle border_color=#C4B5FD "UI/UX дизайнер"
# ... (остальные 48 агентов аналогично)

# === ИТОГО ===
total SHAPE parent=org x=1600 y=800 w=500 h=60 type=round_rectangle fill=#1E293B color=#94A3B8 font=plex_sans size=18 valign=middle border_color=#475569 border_width=2 "<p>📊 51 AI-агент: 1 Оркестратор + 5 × 10</p>"
```

## Результат

Все 63 элемента созданы успешно. URL: `https://miro.com/app/board/uXjVHD9B0oM=/`.
