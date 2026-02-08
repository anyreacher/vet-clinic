# Ветеринарная клиника

Приложение "Ветеринарная Клиника".

Функции: 
  1. Новый пациент.
  2. Запись к врачу (в разработке).
  3. Медицинские карточки (в разработке).

<details>
  <summary>Запуск локально</summary>
  
  1. Клонируйте репозиторий
    
  ```bash
  git clone https://github.com/anyreacher/vet-clinic.git
  ```
  2. Создайте и активируйте venv
  
  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate 
  ```
  3. Установите зависимости
  
  ```bash
  pip install -r requirements.txt
  ```
  4. Скопируйте переменные окружения из .env.example
  
  ```bash
  cp .env.example .env
  ```
  5. Настройте переменные окружения
  
  ```bash
  #.env
  DATABASE_URL=postgresql+asyncpg://<пользователь>:<пароль>@localhost:5432/<название_бд>
  SECRET_KEY=<jwt_токен>
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=15
  REFRESH_TOKEN_EXPIRE_MINUTES=10080
  ```
  
  Сгенерировать jwt-токен можно так:
  ```bash
  openssl rand -hex 32
  ```
  6. Запустите сервер
  ```bash
  fastapi dev
  ```
  7. Приложение доступно по адресу: http://127.0.0.1:8000/

</details>

<details>
  <summary>Запуск через Docker</summary>
  Скоро
</details>
