---
name: miro-board-design
description: "Создание сложных визуальных структур на Miro-досках через layout DSL: оргструктуры, mind maps, диаграммы."
---

# Miro Board Design

Создание сложных визуальных артефактов на Miro-досках с использованием MCP-инструментов Miro. Подходит для: оргструктур, mind maps, диаграмм процессов, стратегических карт.

## Требования

Miro должен быть подключён как MCP-сервер через `hermes mcp` или `hermes config set mcp_servers`.

## Инструменты

| Инструмент | Для чего |
|---|---|
| `mcp_miro_board_create` | Создать новую доску |
| `mcp_miro_board_search_boards` | Найти существующую доску |
| `mcp_miro_code_widget_create` | Добавить Mermaid-диаграмму (mind map, flowchart, sequence) |
| `mcp_miro_doc_create` | Добавить markdown-документ с таблицами и текстом |
| `mcp_miro_layout_get_dsl` | Получить DSL-спецификацию для создания элементов |
| `mcp_miro_layout_create` | Массово создать элементы (shapes, frames, connectors) |
| `mcp_miro_layout_read` | Прочитать структуру существующей доски |
| `mcp_miro_layout_update` | Отредактировать элементы доски |
| `mcp_miro_image_create` | Добавить изображение |
| `mcp_miro_table_create` | Добавить интерактивную таблицу |
| `mcp_miro_comment_create` | Добавить комментарий |
| `mcp_miro_context_get` | Получить AI-обзор содержимого доски |
| `mcp_miro_context_explore` | Обзор high-level элементов доски |

## Рабочий процесс: комплексная структура на доске

### Шаг 1. Создать доску

```python
mcp_miro_board_create(name="Название доски", description="Описание")
# → возвращает miro_url
```

### Шаг 2. Получить DSL-спецификацию (обязательно перед layout_create)

```python
mcp_miro_layout_get_dsl()
# → возвращает полную спецификацию: типы, координаты, цвета, шрифты
```

Ключевые правила координат (из DSL-спецификации):
- **FRAME** на доске: x, y — центр frame, board-absolute координаты
- **SHAPE внутри frame**: x, y — ОТНОСИТЕЛЬНО top-left угла frame. Диапазон: 0 ≤ x ≤ frame_w, 0 ≤ y ≤ frame_h
- **STICKY**: указывается ЛИБО width, ЛИБО height (не оба)
- **DOC/TABLE**: x, y — top-left corner (не центр), в отличие от SHAPE/FRAME/TEXT

### Шаг 3. Создать frame (контейнер)

```
f1 FRAME x=0 y=0 w=3200 h=1800 fill=#0F172A "Название"
```

### Шаг 4. Создать элементы внутри frame

SHAPE для заголовков и блоков:
```
head SHAPE parent=f1 x=1600 y=80 w=440 h=90 type=round_rectangle fill=#7C3AED color=#FFFFFF font=plex_sans size=22 valign=middle border_color=#A78BFA border_width=3 "<p>Заголовок</p>"
```

SHAPE для элементов списка (в колонках по 2):
```
item1 SHAPE parent=f1 x=280 y=420 w=200 h=50 type=rectangle fill=#EDE9FE color=#4C1D95 font=roboto size=10 valign=middle border_color=#C4B5FD "Текст"
item2 SHAPE parent=f1 x=280 y=480 w=200 h=50 type=rectangle fill=#EDE9FE color=#4C1D95 font=roboto size=10 valign=middle border_color=#C4B5FD "Текст"
```

TEXT для подписей:
```
title TEXT parent=f1 x=1600 y=40 w=600 font=open_sans size=24 align=center color=#FFFFFF "Заголовок секции"
```

### Шаг 5. Создать коннекторы (стрелки между элементами)

```
c1 CONNECTOR from=source_alias to=target_alias shape=elbowed stroke_color=#7C3AED end_cap=stealth
c2 CONNECTOR from=source_alias to=target_alias shape=elbowed stroke_color=#2563EB end_cap=stealth
c3 CONNECTOR from=source_alias to=target_alias stroke_style=dashed end_cap=arrow "подпись"
```

Коннекторы создаются ПОСЛЕ всех элементов, так как ссылаются на их alias-ы.

### Шаг 6. (Опционально) Добавить Mermaid-диаграмму

```python
mcp_miro_code_widget_create(
    language="Mermaid",
    code="""mindmap
  root((Центр))
    Ветка1
      Элемент1
      Элемент2
    Ветка2
      Элемент3""",
    miro_url=board_url,
    width=1200, height=800
)
```

### Шаг 7. (Опционально) Добавить markdown-документ

```python
mcp_miro_doc_create(
    content="# Заголовок\n\nТекст и **таблицы**",
    miro_url=board_url,
    x=1300, y=0
)
```

## Планирование координат внутри frame

Для frame размером W×H пикселей, с элементами, размещёнными в N колонок:

```
Колонка K: x = (W / (N+1)) * K
```

Пример для 5 колонок внутри frame 3200×1800:

| Колонка | x | Назначение |
|---|---|---|
| 1 | 280 | Дизайн |
| 2 | 900 | Маркетинг |
| 3 | 1520 | Продажи |
| 4 | 2140 | Разработка |
| 5 | 2760 | Клиенты |

Для двух подколонок в каждой колонке (размещение 10 элементов):
- Левая: x = базовая_x
- Правая: x = базовая_x + 260
- Вертикальный шаг: 60px (элемент 50px + отступ 10px)
- Стартовый y для первой строки: 420
- y для строк 1-5: 420, 480, 540, 600, 660

## Цветовая палитра для департаментов

Рекомендуемые пары (fill / border / text) для светлых блоков на тёмном фоне:

| Назначение | Fill | Border | Text |
|---|---|---|---|
| Фиолетовый | #EDE9FE | #C4B5FD | #4C1D95 |
| Синий | #DBEAFE | #93C5FD | #1E3A8A |
| Зелёный | #D1FAE5 | #6EE7B7 | #064E3B |
| Оранжевый | #FED7AA | #FDBA74 | #7C2D12 |
| Красный | #FECACA | #FCA5A5 | #7F1D1D |

Для заголовков на насыщенном фоне: fill=#7C3AED, color=#FFFFFF.

## Валидация: проверка create

Всегда проверяй результат `layout_create`:
- `success: true` — все элементы созданы
- `created_count: N` — количество созданных элементов
- `failed_items: []` — пустой массив = нет ошибок

Если есть failed_items — смотри в `result_dsl` для диагностики.

## Частые ошибки

1. **Выход за границы frame.** Координаты SHAPE внутри frame — это ЦЕНТР элемента. Элемент с x=3020, w=200 означает, что его левый край на 3020−100=2920, правый на 3020+100=3120. При frame_w=3200 правый край входит (3120 < 3200), но если frame_w=3000 — ошибка.

2. **Не вызван layout_get_dsl перед layout_create.** DSL-формат может меняться. Всегда получай свежую спецификацию перед созданием.

3. **STICKY с width и height одновременно.** Указывается что-то одно.

4. **Коннектор ссылается на несуществующий alias.** Убедись, что все from= и to= ссылаются на alias-ы, объявленные выше в том же DSL.

5. **DOC и TABLE используют x,y как центр вместо top-left.** В отличие от SHAPE, для DOC/TABLE x,y — это верхний левый угол.

## Пример: оргструктура на 51 элемент

См. `references/org-chart-63-items.md` — полный DSL для создания оргструктуры из 1 оркестратора + 5 департаментов × 10 агентов (63 элемента: 1 frame, 56 shapes, 5 connectors, 1 итоговый блок).
