# ============================================
# FILE: app/services/dynamodb_service.py
# ============================================
from typing import List, Optional
import logging
import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from datetime import datetime
from app.models import ReviewFromDB, ReviewSource, ProcessedReview

logger = logging.getLogger(__name__)


class DynamoDBService:
    """
    Сервіс для роботи з DynamoDB
    """

    def __init__(
            self,
            table_name: str,
            region: str,
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None
    ):
        self.table_name = table_name
        self.region = region

        # Ініціалізація boto3 client
        session_params = {'region_name': region}

        if aws_access_key_id and aws_secret_access_key:
            session_params['aws_access_key_id'] = aws_access_key_id
            session_params['aws_secret_access_key'] = aws_secret_access_key

        self.dynamodb = boto3.resource('dynamodb', **session_params)
        self.table = self.dynamodb.Table(table_name)

        logger.info(f"DynamoDBService initialized for table: {table_name} in region: {region}")

    async def get_unprocessed_reviews(self, brand: Optional[str] = None) -> List[ReviewFromDB]:
        """
        Отримує всі відгуки де is_processed = False

        Returns:
            List[ReviewFromDB]: Список необроблених відгуків
        """
        try:
            logger.info(f"Fetching unprocessed reviews from DynamoDB{f' for brand: {brand}' if brand else ''}...")

            # Scan з фільтром на is_processed = False
            filter_expression = Attr('is_processed').eq(False)
            
            # Додаємо фільтр по бренду якщо вказано
            if brand:
                filter_expression = filter_expression & Attr('brand').eq(brand)
            
            response = self.table.scan(
                FilterExpression=filter_expression
            )

            items = response.get('Items', [])

            # Обробка пагінації (якщо є багато записів)
            while 'LastEvaluatedKey' in response:
                logger.info("Fetching next page of results...")
                response = self.table.scan(
                    FilterExpression=filter_expression,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))

            logger.info(f"Found {len(items)} unprocessed reviews in DynamoDB")

            # Конвертуємо в ReviewFromDB моделі
            reviews = []
            for item in items:
                try:
                    review = self._item_to_review(item)
                    reviews.append(review)
                except Exception as e:
                    logger.error(f"Failed to parse review {item.get('id', 'unknown')}: {str(e)}")
                    continue

            logger.info(f"Successfully parsed {len(reviews)} reviews")
            return reviews

        except ClientError as e:
            logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
            raise Exception(f"Failed to fetch reviews from DynamoDB: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def mark_as_processed(self, source: str, review_id: str) -> bool:
        """
        Змінює is_processed на True для конкретного відгуку

        Args:
            source: Джерело відгуку (appstore, googleplay, trustpilot)
            review_id: ID відгуку

        Returns:
            bool: True якщо успішно
        """
        try:
            # Формуємо composite key: source#id (наприклад: appstore#544007664)
            pk = f"{source}#{review_id}"
            logger.info(f"Marking review with pk={pk} as processed...")

            response = self.table.update_item(
                Key={'pk': pk},
                UpdateExpression='SET is_processed = :val',
                ExpressionAttributeValues={':val': True},
                ReturnValues='UPDATED_NEW'
            )

            logger.info(f"Successfully marked review {pk} as processed")
            return True

        except ClientError as e:
            logger.error(f"Failed to update review {pk}: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while updating review {pk}: {str(e)}")
            return False

    async def save_processed_review(self, processed_review: ProcessedReview) -> bool:
        """
        Зберігає оброблений відгук в DynamoDB з новим ключем

        Args:
            processed_review: Оброблений відгук з LLM аналізом

        Returns:
            bool: True якщо успішно
        """
        try:
            # Створюємо новий ID для обробленого відгуку
            processed_id = f"processed_{processed_review.id}"

            logger.info(f"Saving processed review with ID: {processed_id}")

            # Підготовка даних для збереження
            item = {
                'id': processed_id,
                'original_review_id': processed_review.id,
                'source': processed_review.source.value,
                'backlink': processed_review.backlink,
                'text': processed_review.text,
                'rating': processed_review.rating,
                'created_at': processed_review.created_at.isoformat(),
                # LLM аналіз
                'sentiment': processed_review.sentiment.value,
                'description': processed_review.description,
                'category': processed_review.category,
                'is_processed': True,
                # Метадані
                'processed_at': datetime.utcnow().isoformat(),
            }

            # Зберігаємо в DynamoDB
            self.table.put_item(Item=item)

            logger.info(f"Successfully saved processed review {processed_id}")
            return True

        except ClientError as e:
            logger.error(f"Failed to save processed review: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while saving processed review: {str(e)}")
            return False

    async def batch_save_processed_reviews(self, processed_reviews: List[ProcessedReview]) -> dict:
        """
        Масово зберігає оброблені відгуки в DynamoDB

        Args:
            processed_reviews: Список оброблених відгуків

        Returns:
            dict: Статистика операції
        """
        success_count = 0
        failed_count = 0

        for review in processed_reviews:
            result = await self.save_processed_review(review)
            if result:
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"Batch save completed: {success_count} success, {failed_count} failed")

        return {
            "total": len(processed_reviews),
            "success": success_count,
            "failed": failed_count
        }

    async def get_review_by_id(self, source: str, review_id: str) -> Optional[ReviewFromDB]:
        """
        Отримує конкретний відгук за ID

        Args:
            source: Джерело відгуку
            review_id: ID відгуку

        Returns:
            Optional[ReviewFromDB]: Відгук або None
        """
        try:
            pk = f"{source}#{review_id}"
            response = self.table.get_item(Key={'pk': pk})

            if 'Item' not in response:
                logger.warning(f"Review {pk} not found")
                return None

            return self._item_to_review(response['Item'])

        except Exception as e:
            logger.error(f"Failed to get review {pk}: {str(e)}")
            return None

    async def batch_mark_as_processed(self, reviews: List[tuple]) -> dict:
        """
        Масово позначає відгуки як оброблені

        Args:
            reviews: Список кортежів (source, review_id)

        Returns:
            dict: Статистика операції
        """
        success_count = 0
        failed_count = 0

        for source, review_id in reviews:
            result = await self.mark_as_processed(source, review_id)
            if result:
                success_count += 1
            else:
                failed_count += 1

        return {
            "total": len(reviews),
            "success": success_count,
            "failed": failed_count
        }

    def _item_to_review(self, item: dict) -> ReviewFromDB:
        """
        Конвертує DynamoDB item в ReviewFromDB модель
        
        ВАЖЛИВО: Якщо author_hint порожній, але text містить ім'я автора 
        на першому рядку, витягуємо автора з тексту
        """
        # Парсимо дати
        created_at = item.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        fetched_at = item.get('fetched_at')
        if isinstance(fetched_at, str):
            fetched_at = datetime.fromisoformat(fetched_at.replace('Z', '+00:00'))

        # Обробка author_hint та text
        author_hint = item.get('author_hint')
        text = item.get('text', '')
        
        # Якщо author_hint порожній але text містить автора на першому рядку
        if (not author_hint or author_hint.strip() == '') and text and '\n' in text:
            lines = text.split('\n', 1)
            potential_author = lines[0].strip()
            
            # Перевіряємо чи схоже на ім'я (не довше 100 символів)
            if potential_author and len(potential_author) < 100:
                author_hint = potential_author
                text = lines[1].strip() if len(lines) > 1 else text
                logger.debug(f"Extracted author '{author_hint}' from text for review {item.get('id')}")

        return ReviewFromDB(
            id=item['id'],
            source=ReviewSource(item['source']),
            backlink=item['backlink'],
            brand=item['brand'],
            is_processed=item.get('is_processed', False),
            app_identifier=item['app_identifier'],
            title=item.get('title'),
            text=text,
            rating=int(item['rating']) if item.get('rating') is not None and int(item.get('rating', -1)) > 0 else None,
            language=item['language'],
            country=item.get('country'),
            author_hint=author_hint,
            created_at=created_at,
            fetched_at=fetched_at,
            content_hash=item['content_hash']
        )

    async def get_stats(self) -> dict:
        """
        Отримує статистику відгуків

        Returns:
            dict: Статистика
        """
        try:
            # Всі відгуки
            all_response = self.table.scan(Select='COUNT')
            total_count = all_response.get('Count', 0)

            # Необроблені відгуки
            unprocessed_response = self.table.scan(
                FilterExpression=Attr('is_processed').eq(False),
                Select='COUNT'
            )
            unprocessed_count = unprocessed_response.get('Count', 0)

            # Оброблені відгуки
            processed_count = total_count - unprocessed_count

            return {
                "total_reviews": total_count,
                "processed": processed_count,
                "unprocessed": unprocessed_count,
                "processing_rate": round(processed_count / total_count * 100, 2) if total_count > 0 else 0
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {
                "error": str(e)
            }

    async def reset_all_processed_flags(self) -> dict:
        """
        Скидає is_processed = False для ВСІХ записів.
        Використовує scan + batch update.
        
        Returns:
            dict: Статистика операції
        """
        try:
            logger.info("Starting bulk reset of is_processed flags...")
            
            # Отримуємо всі PK (первинні ключі)
            all_keys = []
            response = self.table.scan(
                ProjectionExpression='pk',  # Беремо тільки ключі
                FilterExpression=Attr('is_processed').eq(True)  # Тільки ті, що потрібно скинути
            )
            all_keys.extend(response.get('Items', []))
            
            # Пагінація
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ProjectionExpression='pk',
                    FilterExpression=Attr('is_processed').eq(True),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                all_keys.extend(response.get('Items', []))
            
            total_items = len(all_keys)
            logger.info(f"Found {total_items} processed items to reset")
            
            if total_items == 0:
                return {
                    "success": True,
                    "total_items": 0,
                    "updated": 0,
                    "failed": 0,
                    "message": "No processed items found"
                }
            
            # Batch update по 25 записів (ліміт DynamoDB batch_writer)
            batch_size = 25
            updated_count = 0
            failed_count = 0
            
            for i in range(0, total_items, batch_size):
                batch = all_keys[i:i + batch_size]
                
                try:
                    # Виконуємо batch update
                    for item in batch:
                        try:
                            self.table.update_item(
                                Key={'pk': item['pk']},
                                UpdateExpression='SET is_processed = :val',
                                ExpressionAttributeValues={':val': False}
                            )
                            updated_count += 1
                        except Exception as e:
                            logger.error(f"Failed to update {item['pk']}: {str(e)}")
                            failed_count += 1
                    
                    logger.info(f"Processed batch {i//batch_size + 1}: {updated_count}/{total_items} updated")
                    
                except Exception as e:
                    failed_count += len(batch)
                    logger.error(f"Failed batch {i//batch_size + 1}: {str(e)}")
            
            result = {
                "success": True,
                "total_items": total_items,
                "updated": updated_count,
                "failed": failed_count,
                "message": f"Reset completed: {updated_count} updated, {failed_count} failed"
            }
            
            logger.info(f"Bulk reset completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during bulk reset: {str(e)}")
            raise Exception(f"Failed to reset is_processed flags: {str(e)}")
