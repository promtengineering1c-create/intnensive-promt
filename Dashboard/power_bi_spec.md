# Power BI MVP — спецификация дашборда продаж

## 1. Подготовка данных

1. Power BI Desktop → Get Data → CSV → выбрать `Sales_Data_Cleaned.csv` и `RLS_Access_Cleaned.csv` из папки `output/`.
2. В Power Query проверить типы: `Date` → Date, `Revenue` → Decimal.
3. Убедиться, что связи **не создаются автоматически** через автодетект (мы свяжем вручную через RLS, а не через модель).

---

## 2. Метрики (DAX)

Создать в таблице `Sales_Data_Cleaned` три меры:

### Total Revenue
```
Total Revenue = SUM(Sales_Data_Cleaned[Revenue])
```

### Transaction Count
```
Transaction Count = COUNTROWS(Sales_Data_Cleaned)
```

### Average Order Value (AOV)
```
AOV = DIVIDE([Total Revenue], [Transaction Count], 0)
```

---

## 3. Row-Level Security (RLS)

### Роль «Региональный менеджер»
1. Modeling → Manage Roles → New Role → имя `Regional_Manager`.
2. Выбрать таблицу `RLS_Access_Cleaned` → добавить DAX-фильтр:

```
RLS_Access_Cleaned[Manager_Email] = USERPRINCIPALNAME()
```

3. Выбрать таблицу `Sales_Data_Cleaned` → добавить DAX-фильтр:

```
Sales_Data_Cleaned[Region] IN DISTINCT(RLS_Access_Cleaned[Region])
```

**Логика:** при входе менеджера происходит фильтрация `RLS_Access_Cleaned` по его email, затем `Sales_Data_Cleaned` отсекается по регионам, доступным в отфильтрованной RLS-таблице.

### Роль «Все» (полный доступ)
1. Modeling → Manage Roles → New Role → имя `Full_Access`.
2. В обеих таблицах оставить фильтр пустым (без DAX) — все строки видимы.

---

## 4. Визуализация (3 обязательных элемента)

### Карта (Map / Filled Map)
- **Location:** `Sales_Data_Cleaned[Region]`
- **Bubble size:** `Total Revenue` (мера)
- Bubble size задаёт пузырёк, пропорциональный сумме выручки по региону.

### Линейный график (Line chart)
- **Axis (X):** `Sales_Data_Cleaned[Date]` (иерархия → Date, а не Month/Quarter)
- **Values (Y):** `Total Revenue`
- Опционально: добавить `Transaction Count` второй линией.

### Таблица (Table)
- **Столбцы:** `Transaction_ID`, `Date`, `Region`, `Store`, `Category`, `Revenue`
- Сортировка по `Date` (ascending), по умолчанию.
- Для удобства — включить тоталы по `Revenue` (сумма внизу таблицы).

---

## 5. Проверка RLS в Power BI Desktop

1. Modeling → View as → By Roles
2. Выбрать `Regional_Manager` и указать `msk_manager@company.com`
3. Убедиться, что в карте и таблице видны только строки с `Region = "Москва"`
4. Повторить для других менеджеров из `RLS_Access_Cleaned`
