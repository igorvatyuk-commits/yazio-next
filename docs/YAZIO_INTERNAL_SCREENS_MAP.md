# YAZIO Internal Screens & UI Map

> **Версия приложения:** YAZIO 26.41.2 (`com.yazio.android`)  
> **Устройство / Эмулятор:** `emulator-5554` (Pixel 8, Android 14, разрешение 1080x2400)  
> **Дата съёма данных:** 20 октября 2026 г.  
> **Расположение исходных файлов:**  
> - Скриншоты: `/Users/igorzovnovatuk/.gemini/antigravity/scratch/yazio_research/screens/`  
> - XML-дампы интерфейса: `/Users/igorzovnovatuk/.gemini/antigravity/scratch/yazio_research/ui_dumps/`

---

## 1. Регистрация аккаунта и Paywall-воронка (Screens 30–33)

### `30_account_setup` — Экран создания/входа в аккаунт
- **Файлы:**
  - PNG: `screens/30_account_setup.png`
  - XML: `ui_dumps/30_account_setup.xml`
- **Заголовок:** *"Let’s start tracking"* / *"You’re all set. Time to hit today’s targets and reach your goal."*
- **Ключевые элементы и resource-id:**
  - `login_screen.button.google_login` — Кнопка входа через Google.
  - `login_screen.button.email_login` — Кнопка входа / регистрации по e-mail.
  - `login_screen.button.terms_and_conditions` — Соглашение с условиями обслуживания и политикой конфиденциальности.
- **Статус:** Бесплатно (обязательный шаг создания учетной записи).

---

### `31_paywall_main` — Главный Paywall (предложение YAZIO PRO)
- **Файлы:**
  - PNG: `screens/31_paywall_main.png`
  - XML: `ui_dumps/31_paywall_main.xml`
- **Заголовок:** *"We’ll help you keep your weight steady at 75.0 kg"*
- **Ключевые элементы и тарифные планы:**
  - `shared_element.button.back` / Текст *"Skip"* (координаты `[24, 166][125, 267]`) — Крестик/кнопка пропуска для перехода без подписки.
  - `pro_screen_delighted.button.offer_options_0` — Годовой план: **12 months** (UAH 1,996.00 $\to$ **UAH 999.00**, UAH 83.25/мес) с бейджем *"Most popular"*.
  - `pro_screen_delighted.button.offer_options_1` — Квартальный план: **3 months** (**UAH 499.00**, UAH 166.33/мес).
  - `pro_screen_delighted.section.reviews` — Отзывы реальных пользователей (Adam 24, Chris 53).
  - `pro_screen_delighted.button.continue_button` — Кнопка активации подписки *"Continue"*.
- **Статус:** Платный экран (PRO). Пропускается кнопкой **Skip** в левом верхнем углу.

---

### `32_paywall_scrolled` — Скролл главного Paywall
- **Файлы:**
  - PNG: `screens/32_paywall_scrolled.png`
  - XML: `ui_dumps/32_paywall_scrolled.xml`
- **Ключевые элементы:**
  - Полный обзор блока отзывов и дисклеймера автоматического продления: *"Cancel anytime"*, ссылка `pro_screen_delighted.button.terms_and_condition` (*"Terms of Use & Privacy Policy"*).

---

### `33_paywall_discount_offer` — Скидочный One-Time Offer (Spinning Wheel)
- **Файлы:**
  - PNG: `screens/33_paywall_discount_offer.png`
  - XML: `ui_dumps/33_paywall_discount_offer.xml`
- **Механика и оффер:**
  - Интерактивное «Колесо скидок» (*"Craving a better deal? Spin to get your 75% OFF"* $\to$ *"75% OFF FOREVER"*).
  - `onboarding.card.promotion_price_card` — Спецпредложение: **12 Months за UAH 499.00** (~UAH 41.58/месяц вместо UAH 166.33/мес).
  - `shared_element.button.back` — Кнопка закрытия / пропуска предложения.
- **Статус:** Ограниченный по времени маркетинговый оффер (PRO).

---

## 2. Раздел 1: Дневник (`Diary` tab)

### `40_diary_top` — Верхняя часть дневника
- **Файлы:**
  - PNG: `screens/40_diary_top.png`
  - XML: `ui_dumps/40_diary_top.xml`
- **Ключевые элементы и resource-id:**
  - `diary_screen.button.shop_icon` — Баланс кристаллов/алмазов (*0 diamonds*).
  - `diary_screen.button.streak_icon` — Счетчик серий непрерывного трекинга (*Streaks: 0*).
  - `diary_screen.button.calendar_icon` — Выбор дня / календарь.
  - `diary_screen.card.summary` — Карточка суточного баланса калорий:
    - *Eaten: 0 Cal*
    - *Remaining: 1,838 Cal* (целевая норма по плану)
    - *Burned: 0 Cal*
  - Макронутриенты:
    - *Carbs: 0 / 224 g*
    - *Protein: 0 / 90 g*
    - *Fat: 0 / 59 g*
  - `diary_screen.card.pro` — Промо-баннер скидки на Pro с таймером обратного отсчета (*"Save on Pro: 75% OFF"*).
- **Статус:** Бесплатно (базовый баланс и макросы); персональные расширенные микронутриенты доступны по подписке.

---

### `41_diary_meals_water` — Приёмы пищи и Трекер воды
- **Файлы:**
  - PNG: `screens/41_diary_meals_water.png`
  - XML: `ui_dumps/41_diary_meals_water.xml`
- **Ключевые элементы и resource-id:**
  - `diary_screen.card.nutrition` — Секция питания:
    - `diary_screen.button.food_tracking_add_icon_breakfast` — Завтрак (*Breakfast: 0 / 551 Cal*).
    - `diary_screen.button.food_tracking_add_icon_lunch` — Обед (*Lunch: 0 / 735 Cal*).
    - `diary_screen.button.food_tracking_add_icon_dinner` — Ужин (*Dinner: 0 / 459 Cal*).
    - `diary_screen.button.food_tracking_add_icon_snacks` — Перекусы (*Snacks: 0 / 92 Cal*).
  - `diary_screen.card.water` — Трекер гидратации:
    - `water_card.text.consumed` — Потреблено (*0.00 L*, цель: *2.00 Liters*).
    - `water_card.button.glass_1` ... `water_card.button.glass_8` — Быстрые кнопки добавления стаканов воды (по 250 мл).
    - *"+ Water from food: 0 mL"* — Учёт влаги из съеденных продуктов.
- **Статус:** Добавление еды и базовый трекер воды бесплатны.

---

### `42_diary_bottom_widgets` — Нижняя часть дневника (Вес, Фастинг, Шаги)
- **Файлы:**
  - PNG: `screens/42_diary_bottom_widgets.png`
  - XML: `ui_dumps/42_diary_bottom_widgets.xml`
- **Ключевые элементы и resource-id:**
  - `diary_screen.card.measurement` — Трекер веса: текущий вес 75.0 kg, цель 75.0 kg, ссылка `diary_screen.link.body_values_more` (*More*).
  - `diary_screen.button.fasting_card` — Виджет интервального голодания (*"Manage your fasting routine: Plan and track your fasts"*, кнопка *"Go to Fasting"*).
  - `diary_screen.card.training` — Виджет активности и шагов:
    - Кнопка интеграции с шагомером / Google Fit (*"Connect"*).
    - Кнопка ручного ввода (*"Track steps manually"*).
- **Статус:** Ручной ввод бесплатен; расширенная аналитика трендов веса — PRO.

---

## 3. Раздел 2: Добавление еды (`Add Food` flow)

### `50_add_food_search` — Экран поиска и каталог продуктов
- **Файлы:**
  - PNG: `screens/50_add_food_search.png`
  - XML: `ui_dumps/50_add_food_search.xml`
- **Ключевые элементы и методы ввода:**
  - `food_tracking_screen.card.method_search` — Классический поиск в базе.
  - `food_tracking_screen.card.method_camera` — **AI Camera Tracking** (бейдж *"New"*).
  - `food_tracking_screen.card.method_barcode` — Сканер штрихкодов.
  - `food_tracking_screen.card.method_ai_text_voice` — Ввод голосом / текстом через AI (*"Voice/Text"*).
  - `food_tracking_screen.card.method_more` — Дополнительные инструменты (создание своих блюд, рецепты).
  - `food_tracking_screen.button.search_button` — Поле ввода: *"What did you have for breakfast?"*.
  - Вкладка базы: `food_tracking_screen.dropdown.current_meal_time` с переключением на списки *Frequent*, *Recent*, *Meals*, *Favorites*.
  - Предзаполненный список частых продуктов с калорийностью: *Coffee (2 Cal)*, *Banana (134 Cal)*, *Scrambled Eggs (100 Cal)*, *Strawberries (4 Cal)*.
- **Статус:** Поиск и базовый штрихкод бесплатны.

---

### `51_product_detail_picker` — Карточка продукта (на примере банана)
- **Файлы:**
  - PNG: `screens/51_product_detail_picker.png`
  - XML: `ui_dumps/51_product_detail_picker.xml`
- **Ключевые элементы и resource-id:**
  - Верхняя панель: `foodTime` (выбор приёма пищи), `favorite` (добавить в избранное).
  - Раскладка нутриентов:
    - `energyValue`: **134 Cal**
    - `carbValue`: **34.3 g**
    - `proteinValue`: **1.6 g**
    - `fatValue`: **0.5 g**
    - Индикатор *"Verified nutrition facts"*.
  - `inputArea`:
    - `amountEdit`: ввод количества (по умолчанию `1`).
    - `edit`: выпадающий список единиц измерения (*"Whole, regular (150 g)"*, граммы, штуки, чашки).
  - **PRO-блок:**
    - `header`: *"Food Rating"* — Умный рейтинг полезности продукта (*"Our smart food rating tells you what is good..."*), кнопка `button` (*"Unlock All"* с замком PRO).
  - `addButtonCompose` — Большая зеленая кнопка *"Add"* для сохранения в дневник.
- **Статус:** Добавление продукта и граммовка бесплатны; Food Rating и глубокий микронутриентный анализ — PRO.

---

### `52_barcode_scanner_ui` — Сканер штрихкодов
- **Файлы:**
  - PNG: `screens/52_barcode_scanner_ui.png`
  - XML: `ui_dumps/52_barcode_scanner_ui.xml`
- **Ключевые элементы:**
  - Видоискатель камеры с распознаванием EAN/UPC штрихкодов.
  - Кнопка фонарика (*"Flashlight"*).
  - Заголовок *"Scan a barcode"*, кнопка `shared_element.button.navigation_icon` (*Back*).
- **Статус:** Бесплатно (доступно всем пользователям).

---

### `53_ai_tracking_ui` — Распознавание еды через AI-камеру
- **Файлы:**
  - PNG: `screens/53_ai_tracking_ui.png`
  - XML: `ui_dumps/53_ai_tracking_ui.xml`
- **Заголовок:** *"You snap it, we track it!"*
- **Описание функции:** *"AI-powered photo recognition offers a range of benefits..."*
- **Ключевые элементы:**
  - Интерактивный туториал / промо-экран распознавания готовых блюд и разделения на компоненты.
  - Кнопка `Unlock with Pro` (координаты `[540, 2210]`).
- **Статус:** **PRO-экран** (функция AI-трекинга по фото заблокирована в бесплатной версии).

---

## 4. Раздел 3: Интервальное голодание (`Fasting` tab)

### `60_fasting_overview` — Главный экран трекера голодания
- **Файлы:**
  - PNG: `screens/60_fasting_overview.png`
  - XML: `ui_dumps/60_fasting_overview.xml`
- **Ключевые элементы и resource-id:**
  - Заголовок: `title` (*Fasting*), мотивационный статус `subTitle`.
  - `card` — Карточка таймера текущего протокола:
    - Выбранный протокол: **12:12** (`trackerInfo`).
    - Иконка замка `proLock` на продвинутых фазах.
    - Кнопка `action` — **"START TRACKER"**.
    - Временные рамки: `start` (*Fasting start: Today, 9:00 PM*), `end` (*Fasting end: Tomorrow, 9:00 AM*).
    - `indicator` — Индикаторы фаз автофагии и расщепления жиров.
  - `container` — *"Fasting Quiz: Not sure where to start? Take our quiz to find the fasting type best for you"*.
- **Статус:** Протокол 12:12 и базовый таймер бесплатны.

---

### `61_fasting_detail` — Экран протокола и фаз голодания
- **Файлы:**
  - PNG: `screens/61_fasting_detail.png`
  - XML: `ui_dumps/61_fasting_detail.xml`
- **Ключевые элементы:**
  - Заголовок: **12:12** (*"Our easiest fast. Start here for a gentle introduction"*, теги: *beginner*, *maintain weight*, *blood sugar regulation*).
  - Статистика сообщества: *79,981 fasters*.
  - `fastingTimesRoot` — Интерактивный почасовой график периодов голодания (*Fasting period*) и пищевого окна (*Eating period*).
  - `fastingTimesPickerInclude` — Ручная настройка времени голодания (*"Manually adjust fasting times"*).
  - Секция рекомендаций: *"About This Fast"*, *"Preparing for Your Fast"* (гидратация, электролиты).
  - Кнопка внизу: `start` с текстом **"UNLOCK ALL"** (для перехода на продвинутые протоколы 16:8, 18:6, 20:4, OMAD).
- **Статус:** Базовая справка доступна; сложные протоколы и автоматическая синхронизация таймера — PRO.

---

## 5. Раздел 4: Рецепты (`Recipes` tab)

### `70_recipes_overview` — Каталог рецептов и подборок
- **Файлы:**
  - PNG: `screens/70_recipes_overview.png`
  - XML: `ui_dumps/70_recipes_overview.xml`
- **Ключевые элементы и разделы:**
  - Вкладки: `recipe_screen.tab.discover` (*Discover*), `recipe_screen.tab.favorites` (*My Favorites*).
  - `recipe_screen.section.discover_popular_categories` — Популярные категории:
    - *Breakfast*, *Lunch*, *Dinner*, *Vegan*, *High Protein*.
  - `recipe_screen.section.discover_calorie_counters` — Фильтр по диапазонам калорий:
    - *50–100 Cal*, *100–200 Cal*, *200–300 Cal*, *300–400 Cal*, *400–500 Cal*, *500–600 Cal*.
  - `recipe_screen.section.discover_pick_your_meal` — Выбор рецептов под конкретный приём пищи.
  - Верхняя панель: `recipe_screen.button.basket_icon` (список покупок), `recipe_screen.button.search_icon` (поиск), `recipe_screen.button.more_icon` (фильтры).
- **Статус:** Часть базовых рецептов бесплатна; премиальные коллекции от шеф-поваров, видеоинструкции и автоматический список покупок — PRO.

---

### `71_recipe_detail` — Карточка рецепта (Blueberry Coconut Shake)
- **Файлы:**
  - PNG: `screens/71_recipe_detail.png`
  - XML: `ui_dumps/71_recipe_detail.xml`
- **Ключевые элементы и пищевая ценность:**
  - Заголовок: **Blueberry Coconut Shake**.
  - Метрики: **358 Cal**, время приготовления **5 minutes**, сложность **Easy**.
  - Теги: *Breakfast, Few Ingredients, Fruits, Gluten Free, High Protein, Low Calorie, Pescatarian, Quickly Prepared*.
  - Кнопки действий:
    - *"Add to Grocery List"* — Добавить ингредиенты в список покупок.
    - *"Add to Diary"* — Быстро залогировать порцию рецепта в Дневник с пересчетом всех макросов.
    - Верхние иконки: *Mark as favorite*, *Share*, *Print recipe*.
- **Статус:** Доступен для просмотра и логирования.

---

## 6. Раздел 5: Профиль и Цели (`Profile` tab)

### `80_profile_overview` — Главный экран профиля пользователя
- **Файлы:**
  - PNG: `screens/80_profile_overview.png`
  - XML: `ui_dumps/80_profile_overview.xml`
- **Ключевые элементы и resource-id:**
  - Профиль: имя пользователя (`P_P08`), текущая цель (*Maintain weight*), выбранный план питания (*Classic*).
  - `profile_screen.button.settings_icon` — Переход в настройки (`Settings`).
  - Вкладки: `profile_screen.tab.me` (*Me*), `profile_screen.tab.buddies` (*Buddies* — соцсеть единомышленников).
  - `profile_screen.text.my_overview_sub_header` — Виджет *My overview*, ссылка *Analysis*.
  - Сводка активности дня:
    - *0 Steps*
    - *1,838 Cal left*
  - Блок мотивации: *"Start your streak: Track food daily to keep your streak going"*, кнопка `dialog.button.primary_button` (*Track food*).
- **Статус:** Бесплатно; углубленный аналитический дашборд — PRO.

---

### `81_settings_my_goals` — Настройки целей, калорий и макронутриентов
- **Файлы:**
  - PNG: `screens/81_settings_my_goals.png`, `screens/81_nutrient_goals_detail.png`
  - XML: `ui_dumps/81_settings_my_goals.xml`, `ui_dumps/81_nutrient_goals_detail.xml`
- **Параметры целей:**
  - **Goal:** *Maintain weight*
  - **Starting Weight:** *75.0 kg*
  - **Goal weight:** *75.0 kg*
  - **Activity Level:** *Low*
  - **Calorie Goal:** **1,838 Cal**
  - **Steps:** *10,000*
  - **Nutrient Goals:** *Default*
- **Детализация раскладки макросов (`81_nutrient_goals_detail`):**
  - Углеводы (*Carbs*): **224 g (919 Cal)** $\to$ **50%**
  - Белки (*Protein*): **90 g (368 Cal)** $\to$ **20%**
  - Жиры (*Fat*): **59 g (551 Cal)** $\to$ **30%**
  - Сумма: **100%** (1,838 ккал).
- **Статус:** Просмотр расчетных целей бесплатен; ручная кастомизация целевых процентов БЖУ и включение кето-/низкоуглеводных пресетов — PRO.

---

## 7. Сводная таблица экранов и классификация монетизации

| ID экрана | Название / Назначение | PNG-файл | XML-дамп | Тип доступа |
| :--- | :--- | :--- | :--- | :--- |
| `30_account_setup` | Экран входа / создания аккаунта | `30_account_setup.png` | `30_account_setup.xml` | Бесплатно |
| `31_paywall_main` | Главный Paywall (годовая/3-мес подписка) | `31_paywall_main.png` | `31_paywall_main.xml` | **PRO (Paywall)** |
| `32_paywall_scrolled` | Скролл условий Paywall и отзывы | `32_paywall_scrolled.png` | `32_paywall_scrolled.xml` | **PRO (Paywall)** |
| `33_paywall_discount_offer` | Скидочный оффер (Spinning Wheel 75% OFF) | `33_paywall_discount_offer.png` | `33_paywall_discount_offer.xml` | **PRO (Спецпредложение)** |
| `40_diary_top` | Дневник: кольцо калорий, БЖУ, стрики | `40_diary_top.png` | `40_diary_top.xml` | Бесплатно |
| `41_diary_meals_water` | Дневник: карточки приёмов пищи и вода | `41_diary_meals_water.png` | `41_diary_meals_water.xml` | Бесплатно |
| `42_diary_bottom_widgets` | Дневник: вес, фастинг, шаги | `42_diary_bottom_widgets.png` | `42_diary_bottom_widgets.xml` | Бесплатно |
| `50_add_food_search` | Добавление еды: поиск и быстрые списки | `50_add_food_search.png` | `50_add_food_search.xml` | Бесплатно |
| `51_product_detail_picker` | Карточка продукта: граммовка, БЖУ | `51_product_detail_picker.png` | `51_product_detail_picker.xml` | Бесплатно (Food Rating — PRO) |
| `52_barcode_scanner_ui` | Сканер штрихкодов | `52_barcode_scanner_ui.png` | `52_barcode_scanner_ui.xml` | Бесплатно |
| `53_ai_tracking_ui` | Трекинг еды по фото (AI Camera) | `53_ai_tracking_ui.png` | `53_ai_tracking_ui.xml` | **PRO (Заблокировано)** |
| `60_fasting_overview` | Фастинг: таймер, обзор 12:12 | `60_fasting_overview.png` | `60_fasting_overview.xml` | Бесплатно (12:12) / PRO (16:8+) |
| `61_fasting_detail` | Фастинг: фазы голодания и расписание | `61_fasting_detail.png` | `61_fasting_detail.xml` | Бесплатно / PRO |
| `70_recipes_overview` | Рецепты: каталог, калорийные диапазоны | `70_recipes_overview.png` | `70_recipes_overview.xml` | Бесплатно / PRO-коллекции |
| `71_recipe_detail` | Рецепты: детальная карточка блюда | `71_recipe_detail.png` | `71_recipe_detail.xml` | Бесплатно |
| `80_profile_overview` | Профиль: цели, калории, стрики | `80_profile_overview.png` | `80_profile_overview.xml` | Бесплатно |
| `81_settings_my_goals` | Настройки: калории, вес, макросы БЖУ | `81_settings_my_goals.png` | `81_settings_my_goals.xml` | Бесплатно / PRO |
