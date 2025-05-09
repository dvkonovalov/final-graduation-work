# Проект: Анализ и обработка данных

## Описание

Этот проект предоставляет API для обработки данных постов (например, из социальных сетей) и исторических данных (например, котировок финансовых активов). Он включает в себя несколько шагов предобработки данных, включая сентимент-анализ, тематическое моделирование, а также создание признаков для последующего обучения моделей.

### Включенные функции:
- Сентимент-анализ на основе модели BERT.
- Тематическое моделирование с использованием модели BERTopic.
- Извлечение признаков из временных рядов для анализа.
- Агрегация данных по временным интервалам.
- Обогащение данных с использованием файлов (возможность загрузки данных через путь к файлу).
- Сохранение результатов в CSV файлы для дальнейшего использования.

## Установка

Для работы с проектом потребуется установить несколько зависимостей. Создайте и активируйте виртуальное окружение, затем выполните команду:

```bash
pip install -r requirements.txt
```

## Запуск

Для запуска API используйте команду:

```bash
uvicorn main:app --reload
```

API будет доступно по адресу `http://127.0.0.1:8000`.

## API Endpoints

### 1. `/process-data`
**POST** запрос для обработки списка постов.

#### Описание
Этот endpoint обрабатывает посты, выполняет сентимент-анализ, тематическое моделирование и агрегацию данных по времени. Также добавляются временные признаки и рассчитывается частота появления топовых хэштегов и тем. Помимо данных из тела запроса, можно также передавать данные через файл, указав путь в поле `path`.

#### Входные данные:
```json
{
  "posts": [
    {
      "text": "Текст поста",
      "timestamp": "2025-04-27T12:30:00Z",
      "hashtags": ["#cryptocurrency", "#bitcoin"]
    },
    {
      "text": "Другой текст поста",
      "timestamp": "2025-04-27T12:35:00Z",
      "hashtags": ["#blockchain"]
    }
  ],
  "path": "path/to/your/data.csv"
}
```

#### Ответ:
Если данных меньше 10 записей, возвращается ошибка:
```json
{
  "status": "error",
  "message": "Not enough data. At least 10 records are required."
}
```

Если все прошло успешно:
```json
{
  "status": "success",
  "message": "Data processed and saved to output/processed_posts.csv and output/processed_features.csv",
  "volume_by_time_bucket": {
    "2025-04-27T12:30:00Z": 2,
    "2025-04-27T12:40:00Z": 3
  }
}
```

#### Подробности:
- Выполняется сентимент-анализ с использованием модели BERT для анализа текстов.
- Тематическое моделирование выполняется с использованием **BERTopic**.
- Создаются признаки по времени (например, час дня, день недели).
- Агрегируются данные по времени (например, объем постов в каждом временном интервале, агрегация сентимента).
- Сохраняются два CSV файла:
  - `output/processed_posts.csv`: полный датафрейм с постами и всеми результатами.
  - `output/processed_features.csv`: датафрейм с агрегированными признаками для обучения моделей.

---

### 2. `/upload-historical-data`
**POST** запрос для загрузки исторических данных финансовых активов (например, курсов криптовалют).

#### Описание
Этот endpoint загружает исторические данные о ценах и объеме, выполняет их обработку и сохраняет результат в CSV файл. Данные можно передавать как в теле запроса, так и загружать через путь к файлу, указав его в поле `path`.

#### Входные данные:
```json
{
  "data": [
    {
      "timestamp": "2025-04-27T12:30:00Z",
      "open": 68900.5,
      "high": 69050.0,
      "low": 68800.0,
      "close": 68950.0,
      "volume": 10000.0
    },
    {
      "timestamp": "2025-04-27T12:35:00Z",
      "open": 68950.0,
      "high": 69000.0,
      "low": 68850.0,
      "close": 68975.0,
      "volume": 10500.0
    }
  ],
  "path": "path/to/your/historical_data.csv"
}
```

#### Ответ:
```json
{
  "status": "success",
  "message": "Historical data processed and saved to output/processed_historical_data.csv"
}
```

#### Подробности:
- Обрабатывает данные о котировках (открытие, закрытие, максимум, минимум и объем).
- Если передан путь к дополнительному CSV файлу (в параметре `path`), данные из этого файла будут загружены и объединены с переданными данными.
- Сохранение результата в файл `output/processed_historical_data.csv`.

---

## Примечания

- Входные данные для **/process-data** и **/upload-historical-data** должны быть в формате JSON, где каждый пост или историческая запись включает все необходимые данные.
- Если путь к файлу передан в параметре `path`, данные из этого файла будут добавлены к тем данным, которые переданы в теле запроса.
- Все результаты сохраняются в папке `output`, которая будет создана автоматически, если она еще не существует.

---

## Технические детали

- Для обработки текста используется модель **BERT** (nlptown/bert-base-multilingual-uncased-sentiment) для сентимент-анализа.
- Для тематического моделирования используется **BERTopic** с векторами из **Sentence-BERT**.
- Для агрегации данных по времени и создания признаков используется стандартные функции pandas и времени.
- Для снижения размерности и визуализации используется **UMAP**.

---

## Заключение

Этот проект предоставляет удобный API для обработки и анализа текстовых данных с помощью современных моделей машинного обучения и позволяет создавать признаки для обучения различных моделей. Используемые методы позволяют эффективно извлекать информацию из больших объемов текстовых данных и временных рядов.
