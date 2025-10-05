from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import logging
import traceback

import sys
from pathlib import Path

# Додаємо кореневу директорію в sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.models import (
    CommentInput, DocumentInput, SearchResultInput, ChatMessage,
    GenerateResponseRequest, ResponseDraft, StatisticsResponse,
    CrisisAlert, ExternalReviewsBatch, ReviewFilters, StatisticsFilters,
    BrandComparisonRequest, BrandComparison
)
from app.database import db_manager
from app.analytics import analytics_service
from app.openai_service import openai_service

app = FastAPI(
    title="BrandPulse API",
    description="Brand Reputation Monitoring & Crisis Detection System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "BrandPulse API",
        "version": "1.0.0"
    }


# ==================== COMMENTS ====================

@app.post("/api/reviews/external", response_model=dict)
async def add_external_reviews(data: ExternalReviewsBatch):
    """Додати відгуки у зовнішньому форматі (appstore, googleplay, etc)"""
    try:
        logger.info(f"Received {len(data.reviews)} reviews")
        
        # Маппінг sentiment українською -> англійською
        sentiment_map = {
            "positive": "positive",
            "negative": "negative",
            "neutral": "neutral"
        }
        
        # Маппінг платформ
        platform_map = {
            "appstore": "app_store",
            "googleplay": "google_play",
            "trustpilot": "trustpilot",
            "reddit": "reddit",
            "quora": "quora",
            "news": "news",  # Нова платформа
            "instagram": "instagram"
        }
        
        comment_ids = []
        
        for idx, review in enumerate(data.reviews):
            try:
                logger.info(f"Processing review {idx + 1}/{len(data.reviews)}: {review.id}")
                
                # Конвертуємо timestamp
                try:
                    timestamp = datetime.fromisoformat(review.created_at.replace('Z', '+00:00'))
                except Exception as e:
                    logger.warning(f"Failed to parse timestamp {review.created_at}, using now(). Error: {e}")
                    timestamp = datetime.now()
                
                # Очищення тексту від автора (якщо автор в тексті)
                text = review.text
                author = review.author
                
                # Якщо автор порожній, спробуємо витягти з тексту
                if not author or author.strip() == "":
                    # Шукаємо паттерн: "AUTHOR_NAME\n\n" на початку
                    lines = text.split('\n')
                    if len(lines) > 0:
                        first_line = lines[0].strip()
                        # Якщо перший рядок схожий на нікнейм (без пробілів, великі літери, підкреслення)
                        if first_line and ('_' in first_line or first_line.isupper()) and len(first_line) < 50:
                            author = first_line
                            # Видаляємо перший рядок з тексту
                            text = '\n'.join(lines[1:]).strip()
                            logger.info(f"Extracted author from text: {author}")
                
                # Конвертуємо в наш внутрішній формат
                comment_data = {
                    "brand_name": review.brand,
                    "body": text,  # Використовуємо очищений текст
                    "author": author,  # Використовуємо витягнутого автора
                    "timestamp": timestamp,
                    "rating": float(review.rating) if review.rating is not None else None,  # Опціональний rating
                    "backlink": review.backlink,
                    "platform": platform_map.get(review.source.lower(), "app_store"),
                    "sentiment": sentiment_map.get(review.sentiment.lower(), "neutral"),
                    "llm_description": review.description,
                    "category": review.categories,  # Тепер це масив (categories)
                    "severity": review.severity  # Додаємо severity
                }
                
                logger.info(f"Comment data prepared: platform={comment_data['platform']}, sentiment={comment_data['sentiment']}, categories={len(comment_data['category'])}, severity={comment_data['severity']}, author={comment_data['author']}")
                
                comment_id = db_manager.add_comment(comment_data)
                comment_ids.append(comment_id)
                logger.info(f"Review {review.id} saved with ID: {comment_id}")
                
            except Exception as e:
                logger.error(f"Error processing review {idx + 1} (ID: {review.id}): {str(e)}")
                logger.error(traceback.format_exc())
                # Продовжуємо обробку інших відгуків
                continue
        
        logger.info(f"Successfully processed {len(comment_ids)}/{len(data.reviews)} reviews")
        
        # Автоматична перевірка алертів
        try:
            from app.telegram_service import telegram_service
            
            # Перевіряємо для кожного бренду
            brands_in_batch = set(review.brand for review in data.reviews)
            
            for brand in brands_in_batch:
                alert = analytics_service.check_negative_spike_alert(brand_name=brand)
                if alert:
                    logger.warning(f"Alert detected for brand {brand}: {alert['increase_ratio']:.1f}x increase")
                    # Відправляємо в Telegram
                    telegram_service.send_alert(alert)
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            # Не зупиняємо процес через помилку алертів
        
        return {
            "success": True,
            "added_count": len(comment_ids),
            "comment_ids": comment_ids,
            "message": f"Успішно додано {len(comment_ids)} відгуків"
        }
        
    except Exception as e:
        logger.error(f"Fatal error in add_external_reviews: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/comments", response_model=dict)
async def add_comment(comment: CommentInput):
    """Додати коментар/відгук"""
    try:
        logger.info(f"Adding comment via standard endpoint")
        comment_id = db_manager.add_comment(comment.model_dump())
        logger.info(f"Comment added with ID: {comment_id}")
        return {
            "success": True,
            "comment_id": comment_id,
            "message": "Коментар успішно додано"
        }
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/batch", response_model=dict)
async def add_comments_batch(comments: List[CommentInput]):
    """Додати кілька коментарів одночасно"""
    try:
        logger.info(f"Adding {len(comments)} comments in batch")
        comment_ids = []
        for comment in comments:
            comment_id = db_manager.add_comment(comment.model_dump())
            comment_ids.append(comment_id)
        
        logger.info(f"Added {len(comment_ids)} comments")
        return {
            "success": True,
            "added_count": len(comment_ids),
            "comment_ids": comment_ids
        }
    except Exception as e:
        logger.error(f"Error in batch add: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCUMENTS ====================

@app.post("/api/documents", response_model=dict)
async def add_document(doc: DocumentInput):
    """Додати документ до бази знань"""
    try:
        doc_id = db_manager.add_document(
            title=doc.title,
            content=doc.content,
            doc_type=doc.doc_type,
            metadata=doc.metadata
        )
        return {
            "success": True,
            "document_id": doc_id,
            "message": "Документ успішно додано"
        }
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SERP ====================

@app.post("/api/serp", response_model=dict)
async def add_serp_result(serp: SearchResultInput):
    """Додати результат з Google SERP"""
    try:
        serp_id = db_manager.add_serp_result(serp.model_dump())
        return {
            "success": True,
            "serp_id": serp_id,
            "message": "SERP результат успішно додано"
        }
    except Exception as e:
        logger.error(f"Error adding SERP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/serp/batch", response_model=dict)
async def add_serp_batch(results: List[SearchResultInput]):
    """Додати кілька SERP результатів"""
    try:
        serp_ids = []
        for result in results:
            serp_id = db_manager.add_serp_result(result.model_dump())
            serp_ids.append(serp_id)
        
        return {
            "success": True,
            "added_count": len(serp_ids),
            "serp_ids": serp_ids
        }
    except Exception as e:
        logger.error(f"Error in SERP batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATISTICS ====================

@app.post("/api/statistics", response_model=StatisticsResponse)
async def get_statistics_post(filters: StatisticsFilters = None):
    """Отримати статистику по бренду (POST з фільтрами)"""
    try:
        logger.info(f"Getting statistics with filters: {filters}")
        
        # Конвертуємо фільтри
        filter_dict = None
        if filters:
            filter_dict = {}
            if filters.brand_name:
                filter_dict["brand_name"] = filters.brand_name
            if filters.date_from:
                filter_dict["date_from"] = filters.date_from
            if filters.date_to:
                filter_dict["date_to"] = filters.date_to
            if filters.platforms:
                filter_dict["platforms"] = filters.platforms
        
        stats = analytics_service.get_statistics(filters=filter_dict)
        logger.info(f"Statistics calculated: {stats['total_mentions']} mentions")
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics_get():
    """Отримати статистику по бренду (GET без фільтрів)"""
    try:
        logger.info("Getting statistics (no filters)")
        stats = analytics_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reputation-score")
async def get_reputation_score():
    """Отримати загальну оцінку репутації"""
    try:
        score = analytics_service.calculate_reputation_score()
        return score
    except Exception as e:
        logger.error(f"Error calculating reputation score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CRISIS DETECTION ====================

@app.get("/api/alerts/check")
async def check_alerts(brand_name: str = None):
    """Перевірити алерти про збільшення негативних згадок"""
    try:
        logger.info(f"Checking alerts for brand: {brand_name or 'all'}")
        alert = analytics_service.check_negative_spike_alert(brand_name=brand_name)
        
        if alert:
            logger.warning(f"Alert detected: {alert['increase_ratio']:.1f}x increase")
            return {
                "alert_detected": True,
                "alert": alert
            }
        else:
            logger.info("No alerts detected")
            return {
                "alert_detected": False,
                "message": "Алертів не виявлено"
            }
    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RESPONSE GENERATOR ====================

@app.post("/api/generate-response", response_model=List[ResponseDraft])
async def generate_response(request: GenerateResponseRequest):
    """Згенерувати відповіді на коментар"""
    try:
        logger.info(f"Generating response for comment: {request.comment_id}")
        
        # Отримуємо коментар
        comment = db_manager.get_comment_by_id(request.comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Коментар не знайдено")
        
        brand_name = comment["metadata"].get("brand_name", "Unknown")
        logger.info(f"Generating response for brand: {brand_name}")
        
        # Отримуємо контекст з бази знань
        knowledge = db_manager.search_knowledge(comment["document"], n_results=3)
        knowledge_docs = knowledge.get("documents", [[]])[0] if knowledge.get("documents") else []
        context = "\n".join(knowledge_docs) if knowledge_docs else "Немає додаткового контексту"
        
        # Генеруємо відповіді
        drafts = openai_service.generate_response_drafts(
            comment=comment["document"],
            brand_name=brand_name,
            context=context,
            tones=request.tones,
            tone_adjustment=request.tone_adjustment
        )
        
        logger.info(f"Generated {len(drafts)} response drafts")
        return drafts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CHAT ====================

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Чат про бренд"""
    try:
        logger.info(f"Chat query: {message.message}")
        
        # Детекція запиту на порівняння брендів
        comparison_keywords = ['порівня', 'порівнай', 'порівняти', 'vs', 'проти', 'compare', 'чи краще', 'відмінності']
        is_comparison = any(keyword in message.message.lower() for keyword in comparison_keywords)
        
        if is_comparison:
            # Спробуємо витягнути назви брендів
            all_brands = db_manager.get_all_brands()
            mentioned_brands = []
            
            for brand in all_brands:
                if brand.lower() in message.message.lower():
                    mentioned_brands.append(brand)
            
            if len(mentioned_brands) >= 2:
                logger.info(f"Detected brand comparison: {mentioned_brands}")
                
                # Використовуємо порівняння брендів
                comparisons = analytics_service.compare_brands(mentioned_brands[:5])  # Макс 5 брендів
                
                if not comparisons:
                    return {
                        "answer": f"Не знайдено даних для брендів: {', '.join(mentioned_brands)}",
                        "sources": {"brands_compared": 0}
                    }
                
                # Генеруємо відповідь про порівняння
                answer = openai_service.generate_brand_comparison_answer(comparisons)
                
                return {
                    "answer": answer,
                    "sources": {
                        "brands_compared": len(comparisons),
                        "comparison_data": comparisons
                    }
                }
        
        # Звичайний чат (не порівняння)
        # Збираємо статистику
        stats = analytics_service.get_statistics()
        
        # Шукаємо релевантні коментарі
        relevant_comments = db_manager.search_comments(message.message, n_results=10)
        
        # ChromaDB повертає списки в списках
        docs = relevant_comments.get("documents", [[]])[0] if relevant_comments.get("documents") else []
        metas = relevant_comments.get("metadatas", [[]])[0] if relevant_comments.get("metadatas") else []
        
        comments_text = "\n".join([
            f"- [{m.get('platform')}] ({m.get('sentiment')}): {d[:150]}..."
            for d, m in zip(docs, metas)
        ]) if docs else "Немає релевантних коментарів"
        
        # Шукаємо в базі знань
        knowledge = db_manager.search_knowledge(message.message, n_results=5)
        knowledge_docs = knowledge.get("documents", [[]])[0] if knowledge.get("documents") else []
        knowledge_text = "\n".join(knowledge_docs) if knowledge_docs else "Немає релевантних документів"
        
        # Формуємо контекст
        context_data = {
            "total_mentions": stats["total_mentions"],
            "sentiment_distribution": stats["sentiment_distribution"],
            "top_categories": stats["top_categories"],
            "platform_distribution": stats["platform_distribution"],
            "relevant_comments": comments_text,
            "knowledge_base": knowledge_text
        }
        
        # Отримуємо відповідь від LLM
        answer = openai_service.answer_chat_query(message.message, context_data)
        
        logger.info("Chat response generated successfully")
        
        return {
            "answer": answer,
            "sources": {
                "comments_count": len(docs),
                "knowledge_docs_count": len(knowledge_docs)
            }
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SEARCH ====================

@app.post("/api/reviews/filter")
async def filter_reviews(filters: ReviewFilters):
    """Фільтрація відгуків за різними критеріями"""
    try:
        logger.info(f"Filtering reviews with: brand={filters.brand_name}, severity={filters.severity}, sentiment={filters.sentiment}, categories={filters.categories}")
        
        # Конвертуємо фільтри в dict
        filter_dict = {}
        
        if filters.brand_name:
            filter_dict["brand_name"] = filters.brand_name
        if filters.severity:
            filter_dict["severity"] = filters.severity
        if filters.sentiment:
            filter_dict["sentiment"] = filters.sentiment
        if filters.categories:
            filter_dict["categories"] = filters.categories
        if filters.platforms:
            filter_dict["platforms"] = filters.platforms
        if filters.rating_min is not None:
            filter_dict["rating_min"] = filters.rating_min
        if filters.rating_max is not None:
            filter_dict["rating_max"] = filters.rating_max
        if filters.date_from:
            filter_dict["date_from"] = filters.date_from
        if filters.date_to:
            filter_dict["date_to"] = filters.date_to
        
        filter_dict["limit"] = filters.limit
        filter_dict["offset"] = filters.offset
        filter_dict["sort_by"] = filters.sort_by
        filter_dict["sort_order"] = filters.sort_order
        
        # Фільтруємо
        results = db_manager.filter_comments(filter_dict)
        
        logger.info(f"Filtered {results['filtered_count']} from {results['total']} total reviews")
        
        return {
            "success": True,
            "data": results["results"],
            "pagination": {
                "total": results["total"],
                "filtered_count": results["filtered_count"],
                "returned_count": results["returned_count"],
                "offset": results["offset"],
                "limit": results["limit"],
                "has_more": results["offset"] + results["returned_count"] < results["filtered_count"]
            },
            "filters_applied": filter_dict
        }
        
    except Exception as e:
        logger.error(f"Error filtering reviews: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/comments")
async def search_comments(query: str, limit: int = 10):
    """Пошук по коментарях"""
    try:
        logger.info(f"Searching comments: {query}")
        results = db_manager.search_comments(query, n_results=limit)
        
        # ChromaDB повертає списки в списках
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        docs = results.get("documents", [[]])[0] if results.get("documents") else []
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        
        formatted_results = []
        for i, (doc, metadata) in enumerate(zip(docs, metas)):
            # Конвертуємо category зі строки в масив
            category = metadata.get("category", "")
            category_list = category.split(", ") if category else []
            
            formatted_results.append({
                "id": ids[i],
                "text": doc,
                "platform": metadata.get("platform"),
                "sentiment": metadata.get("sentiment"),
                "timestamp": metadata.get("timestamp"),
                "rating": metadata.get("rating"),
                "category": category_list,
                "severity": metadata.get("severity")
            })
        
        logger.info(f"Found {len(formatted_results)} results")
        
        return {
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results)
        }
    except Exception as e:
        logger.error(f"Error searching comments: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BRANDS MANAGEMENT ====================

@app.get("/api/brands", response_model=List[str])
async def get_all_brands():
    """Отримати список всіх брендів"""
    try:
        logger.info("Getting all brands")
        brands = db_manager.get_all_brands()
        logger.info(f"Found {len(brands)} brands: {brands}")
        return brands
    except Exception as e:
        logger.error(f"Error getting brands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/brands/{brand_name}")
async def delete_brand(brand_name: str):
    """Видалити всі дані по бренду"""
    try:
        logger.info(f"Deleting brand: {brand_name}")
        deleted_count = db_manager.delete_brand_data(brand_name)
        logger.info(f"Deleted {deleted_count} records for brand {brand_name}")
        return {
            "success": True,
            "brand_name": brand_name,
            "deleted_count": deleted_count,
            "message": f"Видалено {deleted_count} записів"
        }
    except Exception as e:
        logger.error(f"Error deleting brand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/brands/compare", response_model=List[BrandComparison])
async def compare_brands(request: BrandComparisonRequest):
    """Порівняння брендів"""
    try:
        logger.info(f"Comparing brands: {request.brand_names}")
        
        filters = {}
        if request.date_from:
            filters["date_from"] = request.date_from
        if request.date_to:
            filters["date_to"] = request.date_to
        
        comparisons = analytics_service.compare_brands(request.brand_names, filters)
        logger.info(f"Generated comparison for {len(comparisons)} brands")
        
        return comparisons
    except Exception as e:
        logger.error(f"Error comparing brands: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    logger.info(f"Starting BrandPulse API on port {settings.PORT}")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
