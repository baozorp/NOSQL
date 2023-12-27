
# Проект "Бронирование комнат"

**Разработчики:** 
- Шекунов Михаил, 
- Лысаковская Екатерина, 
- Сокольский Кирилл

## Задание:

Проект на 2-3 человека. Задача - разработать прототип распределенного приложения для бронирования комнат (квартир, апартаментов, ...)

**Ключевые сущности:**
- Клиент (id, имя)
- Комната (id, адрес, описание, набор атрибутов)
- Бронь (id комнаты, id клиента, даты бронирования, статус бронирования).

**Сценарии:**
1. **Бронирование комнаты.** Клиент после выбора комнаты и дат бронирования, нажимает "бронировать", бронь сохраняется в MongoDB, комната блокируется в Hazelcast. После оплаты (символически), статус брони меняется на "оплачено", комната разблокируется в Hazelcast.
2. **Поиск свободных комнат (Elastic Search).** Поиск по описанию, адресу и датам бронирования. Для удобства поиска по датам, при сохранении брони в MongoDB в ElasticSearch можно индексировать свободные даты.

**План работы:**
1. Обсудить предметную область, детально описать модель хранимых данных.
2. **Разработка:**
   - Заполнить тестовыми данными MongoDB (Клиент, комната)
   - Разработать класс-сервис бронирования
   - Расширить сервис бронирования индексированием данных в ElasticSearch
   - Разработать веб-страницу для бронирования
   - Разработать веб-страницу для поиска комнат
3. **Интеграция и тестирование:**
   - Подготовить данные (порядка десятков тысяч клиентов, десятков тысяч комнат, миллионов броней)
   - Комнаты можно взять отсюда [ссылка](http://insideairbnb.com/get-the-data.html)
   - Клиентов - пользователей Stack Overflow
   - Брони - сгенерировать
   - Функциональное тестирование и исправление ошибок
   - Протестировать поведение системы при отключении одного узла

## Тестирование на отказоустойчивость:

### Тестирование MongoDB:

| Этап | Действие                  | Результат                                                                                                                                                               |
|------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | Отключение одного узла    | Весь функционал работает нормально                                                                                                                                   |
| 2    | Отключение двух узлов      | Весь функционал работает                      |
| 3    | Отключение трех узлов     | Все чтение и запись в MongoDB невозможны. Если данные есть в кэше, их можно получить из него. Поиск по пользователям и сообщениям работают нормально.                   |

### Тестирование Elasticsearch:

| Этап | Действие                  | Результат                                                                                                                                                      |
|------|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1    | Отключение одного узла    | Весь функционал работает нормально.                                                                                                                          |
| 2    | Отключение двух узлов      | Поиск пользователей и сообщений работает нормально. Добавление новых документов невозможно.                                                                   |
| 3    | Отключение трех узлов     | Поиск и добавление новых документов невозможны.                                                                                                              |