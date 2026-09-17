# Red Wine Quality: Automated MLOps Pipeline

Сквозной пайплайн бинарной классификации качества вина ($\ge 6$ — высокое качество, $< 6$ — посредственное) с непрерывной автоматизацией. 

Центральным оркестратором выступает **Apache Airflow**, который каждые 5 минут автоматически инициирует весь цикл:
1. Вызывает **DVC** для очистки данных, фильтрации выбросов, разбиения выборки и обучения логистической регрессии.
2. Фиксирует метрики (Accuracy, F1, ROC-AUC) и параметры в **MLflow** во время выполнения этапа обучения.
3. Пересобирает и запускает изолированные Docker-контейнеры с **FastAPI** и **Streamlit** через **Docker Compose**.

---

## Структура репозитория

```text
├── code
│   ├── datasets
│   │   └── process_data.py       # Стадия 1: очистка и разбиение данных
│   ├── deployment
│   │   ├── api
│   │   │   ├── Dockerfile        # Контейнер сервиса предсказаний
│   │   │   └── main.py           # REST API на FastAPI
│   │   ├── app
│   │   │   ├── Dockerfile        # Контейнер веб-интерфейса
│   │   │   └── app.py            # Веб-приложение на Streamlit
│   │   └── docker-compose.yml    # Конфигурация запуска сервисов
│   └── models
│       └── train.py              # Стадия 2: обучение и логирование в MLflow
├── data
│   ├── processed                 # Папка для train.csv и test.csv
│   └── raw
│       └── winequality-red.csv   # Исходные данные (отслеживаются через DVC)
├── models
│   └── model.pkl                 # Сериализованная модель логистической регрессии
├── services
│   └── airflow
│       ├── dags
│       │   └── wine_pipeline_dag.py # Оркестрирующий DAG (расписание */5 * * * *)
│       └── logs
├── dvc.yaml                      # Спецификация пайплайна DVC
├── requirements.txt              # Зависимости проекта
└── README.md
```

---

## Предварительные требования

- ОС Linux (Ubuntu 22.04 / 24.04), macOS или Windows с WSL2
- Python 3.10 или 3.11
- Установленный Docker Engine и плагин Docker Compose v2

---

## 1. Первоначальная настройка (выполняется один раз)

### Клонирование и установка зависимостей:
```bash
git clone https://github.com/AlfyK1s/assignment1

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Инициализация DVC и фиксация сырых данных:
```bash
# Убедитесь, что winequality-red.csv находится в data/raw/
dvc init
dvc add data/raw/winequality-red.csv
git add data/raw/winequality-red.csv.dvc data/raw/.gitignore
```

### Инициализация Airflow:
```bash
export AIRFLOW_HOME="$(pwd)/services/airflow"
export PROJECT_DIR="$(pwd)"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

source venv/bin/activate
airflow standalone
```

---

## 2. Запуск автоматического пайплайна

Для запуска всей системы (планировщик, API-сервер и UI) достаточно поднять Airflow в standalone-режиме:

```bash
# Переход в репозиторий и активация окружения
cd assignment1
source ../venv/bin/activate

# Переменные окружения
export AIRFLOW_HOME="$(pwd)/services/airflow"
export PROJECT_DIR="$(pwd)"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Единый запуск всех сервисов Airflow
airflow standalone
```

1. Откройте панель управления Airflow: [http://localhost:8080](http://localhost:8080).  
2. Авторизуйтесь с учетными данными `admin` / `admin`.  
3. Найдите в списке DAG `wine_quality_pipeline` и переведите переключатель в положение **ON**.  

Каждые 5 минут Airflow будет автоматически выполнять:
- `dvc repro`: воспроизведение подготовки данных и переобучение модели с сохранением метрик в MLflow.
- `docker compose up -d --build`: сборку и перезапуск Docker-контейнеров инференса и интерфейса.

---

## 3. Мониторинг и проверка работы

- **Веб-интерфейс Streamlit**: [http://localhost:8501](http://localhost:8501)  
  Форма ввода параметров вина с кнопкой для получения класса и вероятности.
- **Интерактивная документация FastAPI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
  Проверка методов `GET /health` и `POST /predict`.
- **Дашборд экспериментов MLflow** (запуск при необходимости анализа метрик):
  ```bash
  mlflow ui --port 5000
  ```
  Интерфейс доступен по адресу [http://localhost:5000](http://localhost:5000).

---

## 4. Остановка сервисов

```bash
# Остановка Docker-контейнеров приложения
cd code/deployment && docker compose down

# Остановка процессов Airflow
pkill -f "airflow scheduler"
pkill -f "airflow webserver"
