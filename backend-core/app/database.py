import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import json


class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Ініціалізація колекцій
        self.comments_collection = self.client.get_or_create_collection(
            name=settings.COMMENTS_COLLECTION,
            metadata={"description": "User comments and reviews"}
        )
        
        self.documents_collection = self.client.get_or_create_collection(
            name=settings.DOCUMENTS_COLLECTION,
            metadata={"description": "Brand documents and knowledge base"}
        )
        
        self.serp_collection = self.client.get_or_create_collection(
            name=settings.SERP_COLLECTION,
            metadata={"description": "Google SERP results"}
        )
    
    def add_comment(self, comment_data: dict) -> str:
        """Додати коментар до ChromaDB"""
        comment_id = str(uuid.uuid4())
        
        # Підготовка метаданих (ChromaDB підтримує тільки str, int, float, bool)
        # Категорії конвертуємо в строку через кому
        category = comment_data.get("category", "general")
        if isinstance(category, list):
            category = ", ".join(category)
        
        metadata = {
            "brand_name": comment_data.get("brand_name", "Unknown"),  # Додаємо brand_name
            "author": comment_data.get("author", ""),  # Додаємо author
            "platform": comment_data["platform"],
            "sentiment": comment_data["sentiment"],
            "timestamp": comment_data["timestamp"].isoformat(),
            "rating": float(comment_data.get("rating", 0)) if comment_data.get("rating") else 0.0,
            "category": category,
            "severity": comment_data.get("severity", "medium"),
            "backlink": comment_data.get("backlink", ""),
        }
        
        # Формування тексту для embedding
        full_text = f"{comment_data['body']}"
        if comment_data.get("llm_description"):
            full_text += f"\n\nОпис: {comment_data['llm_description']}"
        
        self.comments_collection.add(
            ids=[comment_id],
            documents=[full_text],
            metadatas=[metadata]
        )
        
        return comment_id
    
    def add_document(self, title: str, content: str, doc_type: str = "general", metadata: dict = None) -> str:
        """Додати документ до бази знань"""
        doc_id = str(uuid.uuid4())
        
        doc_metadata = {
            "title": title,
            "doc_type": doc_type,
            "timestamp": datetime.now().isoformat(),
        }
        
        if metadata:
            # Додаємо тільки підтримувані типи
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    doc_metadata[key] = value
        
        self.documents_collection.add(
            ids=[doc_id],
            documents=[f"{title}\n\n{content}"],
            metadatas=[doc_metadata]
        )
        
        return doc_id
    
    def add_serp_result(self, serp_data: dict) -> str:
        """Додати результат з Google SERP"""
        serp_id = str(uuid.uuid4())
        
        metadata = {
            "query": serp_data["query"],
            "title": serp_data["title"],
            "url": serp_data["url"],
            "position": int(serp_data["position"]),
            "timestamp": serp_data["timestamp"].isoformat(),
        }
        
        self.serp_collection.add(
            ids=[serp_id],
            documents=[f"{serp_data['title']}\n{serp_data['snippet']}"],
            metadatas=[metadata]
        )
        
        return serp_id
    
    def search_comments(self, query: str, n_results: int = 10, filter_dict: dict = None) -> dict:
        """Пошук по коментарях"""
        results = self.comments_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_dict if filter_dict else None
        )
        return results
    
    def search_knowledge(self, query: str, n_results: int = 5) -> dict:
        """Пошук по базі знань"""
        results = self.documents_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_all_comments(self, limit: int = 1000) -> dict:
        """Отримати всі коментарі"""
        results = self.comments_collection.get(limit=limit)
        return results
    
    def get_comments_by_timerange(self, start_time: datetime, end_time: datetime) -> dict:
        """Отримати коментарі за часовий проміжок"""
        all_comments = self.get_all_comments()
        
        filtered_ids = []
        filtered_docs = []
        filtered_metadata = []
        
        for i, metadata in enumerate(all_comments.get("metadatas", [])):
            comment_time = datetime.fromisoformat(metadata["timestamp"])
            if start_time <= comment_time <= end_time:
                filtered_ids.append(all_comments["ids"][i])
                filtered_docs.append(all_comments["documents"][i])
                filtered_metadata.append(metadata)
        
        return {
            "ids": filtered_ids,
            "documents": filtered_docs,
            "metadatas": filtered_metadata
        }
    
    def get_comment_by_id(self, comment_id: str) -> Optional[dict]:
        """Отримати коментар по ID"""
        try:
            result = self.comments_collection.get(ids=[comment_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
        except:
            pass
        return None
    
    def filter_comments(self, filters: dict) -> dict:
        """Фільтрація коментарів за різними критеріями"""
        # Отримуємо всі коментарі
        all_comments = self.get_all_comments(limit=10000)
        
        if not all_comments["ids"]:
            return {
                "results": [],
                "total": 0,
                "filtered_count": 0
            }
        
        # Фільтруємо коментарі
        filtered_results = []
        
        for i, (comment_id, document, metadata) in enumerate(zip(
            all_comments["ids"],
            all_comments["documents"],
            all_comments["metadatas"]
        )):
            # Фільтр по brand_name
            if filters.get("brand_name"):
                if metadata.get("brand_name") != filters["brand_name"]:
                    continue
            
            # Фільтр по severity
            if filters.get("severity"):
                if metadata.get("severity") not in filters["severity"]:
                    continue
            
            # Фільтр по sentiment
            if filters.get("sentiment"):
                if metadata.get("sentiment") not in filters["sentiment"]:
                    continue
            
            # Фільтр по platforms
            if filters.get("platforms"):
                if metadata.get("platform") not in filters["platforms"]:
                    continue
            
            # Фільтр по categories (хоча б одна категорія збігається)
            if filters.get("categories"):
                comment_categories = metadata.get("category", "").split(", ")
                if not any(cat in filters["categories"] for cat in comment_categories):
                    continue
            
            # Фільтр по rating
            rating = metadata.get("rating", 0)
            if filters.get("rating_min") is not None:
                if rating < filters["rating_min"]:
                    continue
            if filters.get("rating_max") is not None:
                if rating > filters["rating_max"]:
                    continue
            
            # Фільтр по даті
            if filters.get("date_from") or filters.get("date_to"):
                try:
                    from datetime import timezone
                    timestamp_str = metadata["timestamp"]
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    # Нормалізуємо timezone
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                except:
                    continue
                
                if filters.get("date_from"):
                    try:
                        date_from = datetime.fromisoformat(filters["date_from"].replace('Z', '+00:00'))
                        if date_from.tzinfo is None:
                            date_from = date_from.replace(tzinfo=timezone.utc)
                        if timestamp < date_from:
                            continue
                    except:
                        pass
                
                if filters.get("date_to"):
                    try:
                        date_to = datetime.fromisoformat(filters["date_to"].replace('Z', '+00:00'))
                        if date_to.tzinfo is None:
                            date_to = date_to.replace(tzinfo=timezone.utc)
                        if timestamp > date_to:
                            continue
                    except:
                        pass
            
            # Додаємо до результатів
            filtered_results.append({
                "id": comment_id,
                "brand_name": metadata.get("brand_name", "Unknown"),
                "text": document,
                "author": metadata.get("author", ""),
                "platform": metadata.get("platform"),
                "sentiment": metadata.get("sentiment"),
                "severity": metadata.get("severity"),
                "category": metadata.get("category", "").split(", ") if metadata.get("category") else [],
                "rating": metadata.get("rating"),
                "timestamp": metadata.get("timestamp"),
                "backlink": metadata.get("backlink")
            })
        
        # Сортування
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        sort_by = filters.get("sort_by", "timestamp")
        sort_order = filters.get("sort_order", "desc")
        reverse = (sort_order == "desc")
        
        if sort_by == "severity":
            filtered_results.sort(
                key=lambda x: severity_order.get(x.get("severity", "low"), 0),
                reverse=reverse
            )
        elif sort_by == "rating":
            filtered_results.sort(
                key=lambda x: x.get("rating", 0),
                reverse=reverse
            )
        else:  # timestamp
            filtered_results.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=reverse
            )
        
        # Пагінація
        offset = filters.get("offset", 0)
        limit = filters.get("limit", 100)
        
        paginated_results = filtered_results[offset:offset + limit]
        
        return {
            "results": paginated_results,
            "total": len(all_comments["ids"]),
            "filtered_count": len(filtered_results),
            "returned_count": len(paginated_results),
            "offset": offset,
            "limit": limit
        }

    def get_all_brands(self) -> List[str]:
        """Отримати список всіх брендів"""
        all_comments = self.get_all_comments(limit=10000)
        brands = set()
        for metadata in all_comments.get("metadatas", []):
            brand = metadata.get("brand_name")
            if brand:
                brands.add(brand)
        return sorted(list(brands))
    
    def delete_brand_data(self, brand_name: str) -> int:
        """Видалити всі дані по бренду"""
        all_comments = self.get_all_comments(limit=10000)
        ids_to_delete = []
        
        for i, metadata in enumerate(all_comments.get("metadatas", [])):
            if metadata.get("brand_name") == brand_name:
                ids_to_delete.append(all_comments["ids"][i])
        
        if ids_to_delete:
            self.comments_collection.delete(ids=ids_to_delete)
        
        return len(ids_to_delete)


# Singleton instance
db_manager = ChromaDBManager()
