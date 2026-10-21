# MaxStriX324 — personal website

Исходный код моего персонального сайта: **[maxstrix324.github.io](https://maxstrix324.github.io/)**.

Я — **Максим Стародуб (MaxStriX324)**. Инженер-схемотехник, самодельщик и разработчик. Основные интересы — embedded systems, силовая электроника, электропривод, автомобильная техника, автоматизация и путешествия.

## Структура

- **Главная** — краткое знакомство, направления работы, избранные проекты, путешествия и публичные ресурсы;
- **About** — подробная биография: от первых программ и автомобильных проектов до профессиональной схемотехники и электропривода;
- **Privacy** — информация о статистике и настройках согласия;
- **Projects** — аппаратные, программные и автомобильные проекты с внешними ссылками на GitHub и DRIVE2;
- **Автоматизация лаборатории** — KiCad SVG → LaserGRBL, KiCad DRL → CNC3018 и автоматический архив осциллограмм Rigol;
- **Traction Inverter case study** — отдельная техническая страница с архитектурой тягового IGBT-инвертора.

## Темы

`STM32` · `C` · `Python` · `Kotlin` · `CAN` · `RS-485` · `KiCad` · `Power Electronics` · `Electric Drives` · `EV` · `Automotive` · `Automation` · `Reverse Engineering`

## Отдельный веб-проект

**900 рук** — бесплатная афиша мероприятий Саратовской области. Проект включает веб-приложение, PostgreSQL, Docker, Caddy и self-hosted инфраструктуру на Linux.

## Технически

Сайт намеренно остаётся простым:

- чистые HTML и CSS;
- адаптивная вёрстка;
- без фреймворков и обязательного JavaScript;
- опциональные Google Analytics 4 и Яндекс.Метрика (после настройки отдельных ID); аналитические скрипты загружаются только с согласия посетителя;
- публикация через GitHub Pages.

## Публичные ресурсы

- [GitHub](https://github.com/MaxStriX324)
- [Habr](https://habr.com/ru/users/MaxStriX324/)
- [DRIVE2](https://www.drive2.ru/users/maxstrix324/)
- [Пикабу](https://pikabu.ru/@MaxStriX324)
- [YouTube](https://www.youtube.com/@MaxStriX324)
- [RUTUBE](https://rutube.ru/channel/6327951/)
- [Дзен](https://dzen.ru/maxstrix324)
- [Instagram](https://www.instagram.com/maxstrix324/)
- [Telegram](https://t.me/MaxStriX324)
- [VK](https://vk.ru/maxstrix324)
- [StrixGarage64](https://vk.com/strixgarage64)

Сайт будет дополняться подробными страницами отдельных проектов и техническими заметками.

## Аналитика личного сайта

Все HTML-страницы подключают `assets/analytics.js`, где задаются `googleMeasurementId` (`G-...`) и `yandexCounterId` (положительное целое число). Не использовать ID от 900pyk.club. Пока оба поля пусты, аналитические скрипты не загружаются и баннер не показывается. После заполнения — согласие opt-in, можно отозвать в футере. Настройки GA4/Yandex: отдельные счётчики для `maxstrix324.github.io`; в Метрике создайте цель JavaScript-события `github_repository_click`, а в GA4 при необходимости зарегистрируйте пользовательский параметр события `repository` для детализации отчётов.
