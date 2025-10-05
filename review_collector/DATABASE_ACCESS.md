# 🔐 Доступ до DynamoDB з Інтернету

Гайд по підключенню до DynamoDB бази даних з зовнішніх клієнтів (не через Lambda/API Gateway).

---

## 📊 Інформація про базу даних

- **Тип:** AWS DynamoDB
- **Назва таблиці:** `ReviewsTable`
- **Регіон:** Ваш AWS регіон (перевірити через `aws configure get region`)
- **Partition Key:** `pk` (String) - формат: `source#id` (наприклад: `appstore#12345`)
- **GSI:** `brand-created_at-index` для запитів за брендом

---

## 🌐 Варіант 1: AWS CLI (найпростіший)

### Передумови
```bash
# Встановити AWS CLI
brew install awscli  # macOS
# або: pip install awscli

# Налаштувати credentials
aws configure
# Введіть: Access Key ID, Secret Access Key, Region, Output format
```

### Приклади запитів

#### Отримати всі відгуки бренду
```bash
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand":{"S":"telegram"}}' \
  --limit 10
```

#### Отримати конкретний відгук
```bash
aws dynamodb get-item \
  --table-name ReviewsTable \
  --key '{"pk":{"S":"appstore#544007664"}}'
```

#### Scan всієї таблиці (обережно - дорого!)
```bash
aws dynamodb scan \
  --table-name ReviewsTable \
  --limit 10
```

---

## 🐍 Варіант 2: Python boto3 (програмний доступ)

### Встановлення
```bash
pip install boto3
```

### Приклад скрипта

```python
import boto3
from boto3.dynamodb.conditions import Key

# Ініціалізація клієнта
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Ваш регіон
table = dynamodb.Table('ReviewsTable')

# 1. Отримати відгуки за брендом
def get_reviews_by_brand(brand, limit=100):
    response = table.query(
        IndexName='brand-created_at-index',
        KeyConditionExpression=Key('brand').eq(brand),
        ScanIndexForward=False,  # Від новіших до старіших
        Limit=limit
    )
    return response['Items']

# 2. Отримати конкретний відгук
def get_review_by_id(source, review_id):
    pk = f"{source}#{review_id}"
    response = table.get_item(Key={'pk': pk})
    return response.get('Item')

# 3. Отримати всі відгуки (пагінація)
def get_all_reviews(limit=100):
    response = table.scan(Limit=limit)
    return response['Items']

# Використання
if __name__ == '__main__':
    # Приклад 1: Відгуки Telegram
    reviews = get_reviews_by_brand('telegram', limit=10)
    print(f"Знайдено {len(reviews)} відгуків")
    
    for review in reviews:
        print(f"- {review['rating']}★ {review.get('title', 'No title')}")
    
    # Приклад 2: Конкретний відгук
    review = get_review_by_id('appstore', '544007664')
    if review:
        print(f"Відгук: {review}")
```

---

## 🔑 Варіант 3: IAM користувач з обмеженими правами

Для безпечного доступу створіть окремого IAM користувача з обмеженими правами.

### Крок 1: Створити IAM користувача

```bash
# Створити користувача
aws iam create-user --user-name dynamodb-readonly-user

# Створити Access Key
aws iam create-access-key --user-name dynamodb-readonly-user
# ЗБЕРЕЖІТЬ AccessKeyId та SecretAccessKey!
```

### Крок 2: Створити політику з обмеженими правами

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/ReviewsTable",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/ReviewsTable/index/*"
      ]
    }
  ]
}
```

Збережіть як `dynamodb-readonly-policy.json` та застосуйте:

```bash
# Створити політику
aws iam create-policy \
  --policy-name DynamoDBReviewsReadOnly \
  --policy-document file://dynamodb-readonly-policy.json

# Прикріпити до користувача
aws iam attach-user-policy \
  --user-name dynamodb-readonly-user \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/DynamoDBReviewsReadOnly
```

### Крок 3: Використовувати credentials

```python
import boto3

# Опція А: Через environment variables
import os
os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_ACCESS_KEY'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_SECRET_KEY'

# Опція Б: Через конфіг
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)

table = dynamodb.Table('ReviewsTable')
```

---

## 🌍 Варіант 4: Через API Gateway (рекомендовано)

Якщо у проекті вже є API Gateway, використовуйте HTTP endpoints (безпечніше):

```bash
# Після `cdk deploy` отримаєте URL:
API_URL="https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/"

# Приклад 1: Отримати відгуки за брендом
curl "${API_URL}reviews/brand/telegram?limit=50"

# Приклад 2: Отримати конкретний відгук
curl "${API_URL}reviews/appstore/544007664"

# Приклад 3: З Python
import requests

response = requests.get(f"{API_URL}reviews/brand/telegram", params={'limit': 50})
reviews = response.json()
print(f"Знайдено: {reviews['count']} відгуків")
```

---

## 📱 Варіант 5: NoSQL Workbench (GUI клієнт)

AWS надає безкоштовний GUI клієнт для DynamoDB.

### Встановлення
1. Завантажити: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html
2. Встановити на macOS/Windows/Linux
3. Додати AWS credentials через Settings

### Підключення
1. Відкрити NoSQL Workbench
2. **Operation builder** → **Add connection**
3. Вибрати **DynamoDB local** або **AWS**
4. Ввести Access Key ID + Secret Access Key
5. Вибрати регіон
6. Підключитися до таблиці `ReviewsTable`

Тепер можна:
- ✅ Переглядати дані в таблиці
- ✅ Виконувати Query/Scan
- ✅ Фільтрувати за атрибутами
- ✅ Експортувати в JSON/CSV

---

## 🔒 Безпека: Що потрібно знати

### ⚠️ DynamoDB не має "публічного IP"
DynamoDB - це managed сервіс AWS. Доступ завжди йде через:
- AWS API endpoints (через HTTPS)
- IAM authentication (Access Keys / IAM Roles)

### ✅ Best Practices

1. **Ніколи не хардкодьте credentials в коді**
   ```python
   # ❌ ПОГАНО
   aws_access_key_id='AKIAIOSFODNN7EXAMPLE'
   
   # ✅ ДОБРЕ - через env vars або AWS credentials file
   ```

2. **Використовуйте read-only користувачів**
   - Для читання даних створюйте окремих IAM користувачів без прав на write/delete

3. **Обмежуйте IP адреси (опціонально)**
   ```json
   {
     "Condition": {
       "IpAddress": {
         "aws:SourceIp": "YOUR.PUBLIC.IP/32"
       }
     }
   }
   ```

4. **Використовуйте VPC Endpoints (для production)**
   - Якщо доступ потрібен з EC2/Lambda - використовуйте VPC Endpoints
   - Не потрібен інтернет-доступ

---

## 📊 Структура даних в DynamoDB

### Формат записів

```json
{
  "pk": "appstore#12345",
  "id": "12345",
  "source": "appstore",
  "brand": "telegram",
  "app_identifier": "544007664",
  "title": "Great app!",
  "text": "Love using this messenger...",
  "rating": 5,
  "language": "en",
  "country": "US",
  "author_hint": "JohnDoe",
  "created_at": "2024-01-15T10:30:00",
  "fetched_at": "2024-01-15T12:00:00",
  "content_hash": "abc123...",
  "backlink": "https://apps.apple.com/..."
}
```

### Індекси

1. **Primary Key:** `pk` (формат: `source#id`)
2. **GSI:** `brand-created_at-index`
   - Partition key: `brand`
   - Sort key: `created_at`

---

## 🚀 Швидкий старт

### Python скрипт для читання

```python
#!/usr/bin/env python3
"""
Простий скрипт для читання відгуків з DynamoDB
"""
import boto3
from boto3.dynamodb.conditions import Key
import json

def main():
    # Підключення
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('ReviewsTable')
    
    # Запит відгуків
    brand = input("Введіть бренд (наприклад, telegram): ")
    limit = int(input("Скільки відгуків показати? (1-100): ") or "10")
    
    response = table.query(
        IndexName='brand-created_at-index',
        KeyConditionExpression=Key('brand').eq(brand),
        Limit=limit
    )
    
    reviews = response['Items']
    
    print(f"\n✅ Знайдено {len(reviews)} відгуків для {brand}:\n")
    
    for i, review in enumerate(reviews, 1):
        print(f"{i}. {'⭐' * review['rating']} ({review['rating']}/5)")
        print(f"   {review.get('title', 'Без заголовка')}")
        print(f"   Джерело: {review['source']}")
        print(f"   Дата: {review['created_at']}")
        print()

if __name__ == '__main__':
    main()
```

Збережіть як `read_reviews.py` та запустіть:
```bash
python read_reviews.py
```

---

## 🆘 Troubleshooting

### Помилка: `Unable to locate credentials`
```bash
# Перевірити поточні credentials
aws sts get-caller-identity

# Налаштувати заново
aws configure
```

### Помилка: `AccessDeniedException`
Ваш IAM користувач не має прав. Додайте політику:
```bash
aws iam attach-user-policy \
  --user-name YOUR_USER \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess
```

### Помилка: `ResourceNotFoundException`
Перевірте:
- Чи правильна назва таблиці (`ReviewsTable`)
- Чи правильний регіон
- Чи таблиця існує: `aws dynamodb list-tables`

---

## 📚 Корисні посилання

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Boto3 DynamoDB Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html)
- [NoSQL Workbench](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

---

## 💡 Рекомендації

Для різних сценаріїв:

| Сценарій | Рекомендований спосіб |
|----------|----------------------|
| Швидкий перегляд даних | AWS CLI або NoSQL Workbench |
| Інтеграція в застосунок | Python boto3 + IAM користувач |
| Публічний доступ | API Gateway (POST/GET endpoints) |
| Аналітика/BI інструменти | AWS Glue + Athena + QuickSight |
| Локальна розробка | DynamoDB Local + NoSQL Workbench |

---

**Створено для Review Collector Project**  
*Безпечний доступ до DynamoDB з будь-якої точки світу* 🌍

