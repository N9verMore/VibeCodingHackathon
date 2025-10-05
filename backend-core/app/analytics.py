from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from app.database import db_manager
from app.config import settings
from app.models import CrisisLevel, CrisisAlert, Platform
from app.openai_service import openai_service


class AnalyticsService:
    
    def calculate_reputation_score(self) -> dict:
        """Розраховує загальну оцінку репутації (0-100)"""
        all_comments = db_manager.get_all_comments()
        
        if not all_comments["metadatas"]:
            return {
                "overall_score": 50.0,
                "trend": "stable",
                "risk_level": CrisisLevel.LOW,
                "platform_scores": {},
                "last_updated": datetime.now()
            }
        
        # Підрахунок по sentiment
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        platform_sentiments = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0})
        ratings = []
        
        for metadata in all_comments["metadatas"]:
            sentiment = metadata.get("sentiment", "neutral")
            platform = metadata.get("platform", "unknown")
            rating = metadata.get("rating", 0)
            
            sentiment_counts[sentiment] += 1
            platform_sentiments[platform][sentiment] += 1
            platform_sentiments[platform]["total"] += 1
            
            if rating > 0:
                ratings.append(rating)
        
        total = sum(sentiment_counts.values())
        if total == 0:
            return {
                "overall_score": 50.0,
                "trend": "stable",
                "risk_level": CrisisLevel.LOW,
                "platform_scores": {},
                "last_updated": datetime.now()
            }
        
        # Базовий розрахунок: позитив +1, нейтрал 0, негатив -1
        score = (
            (sentiment_counts["positive"] * 1.0 + 
             sentiment_counts["neutral"] * 0.5 + 
             sentiment_counts["negative"] * 0.0) / total
        ) * 100
        
        # Якщо є рейтинги, враховуємо їх
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            rating_score = (avg_rating / 5.0) * 100
            score = (score * 0.6 + rating_score * 0.4)  # 60% sentiment, 40% rating
        
        # Розрахунок тренду (порівняння останніх 7 днів з попередніми 7)
        trend = self._calculate_trend(all_comments)
        
        # Визначення рівня ризику
        negative_ratio = sentiment_counts["negative"] / total if total > 0 else 0
        if negative_ratio > 0.6:
            risk_level = CrisisLevel.HIGH
        elif negative_ratio > 0.4:
            risk_level = CrisisLevel.MEDIUM
        else:
            risk_level = CrisisLevel.LOW
        
        # Розрахунок по платформах
        platform_scores = {}
        for platform, sentiments in platform_sentiments.items():
            if sentiments["total"] > 0:
                platform_score = (
                    (sentiments["positive"] * 1.0 + 
                     sentiments["neutral"] * 0.5) / sentiments["total"]
                ) * 100
                platform_scores[platform] = round(platform_score, 1)
        
        return {
            "overall_score": round(score, 1),
            "trend": trend,
            "risk_level": risk_level,
            "platform_scores": platform_scores,
            "last_updated": datetime.now()
        }
    
    def _calculate_trend(self, all_comments: dict) -> str:
        """Визначає тренд репутації"""
        from datetime import timezone
        
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        recent_score = 0
        previous_score = 0
        recent_count = 0
        previous_count = 0
        
        for metadata in all_comments["metadatas"]:
            timestamp_str = metadata["timestamp"]
            
            # Парсимо timestamp і нормалізуємо до UTC
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                # Якщо немає timezone - додаємо UTC
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
            except:
                continue
            
            sentiment = metadata.get("sentiment", "neutral")
            sentiment_value = {"positive": 1, "neutral": 0.5, "negative": 0}[sentiment]
            
            if timestamp > week_ago:
                recent_score += sentiment_value
                recent_count += 1
            elif timestamp > two_weeks_ago:
                previous_score += sentiment_value
                previous_count += 1
        
        if recent_count == 0 or previous_count == 0:
            return "stable"
        
        recent_avg = recent_score / recent_count
        previous_avg = previous_score / previous_count
        
        if recent_avg > previous_avg + 0.1:
            return "up"
        elif recent_avg < previous_avg - 0.1:
            return "down"
        else:
            return "stable"
    
    def get_statistics(self, filters: dict = None) -> dict:
        """Повертає повну статистику з можливістю фільтрації"""
        all_comments = db_manager.get_all_comments()
        
        # Фільтруємо коментарі якщо є фільтри
        if filters:
            filtered_ids = []
            filtered_docs = []
            filtered_metas = []
            
            for i, metadata in enumerate(all_comments["metadatas"]):
                # Фільтр по brand_name
                if filters.get("brand_name"):
                    if metadata.get("brand_name") != filters["brand_name"]:
                        continue
                
                # Фільтр по даті
                if filters.get("date_from") or filters.get("date_to"):
                    try:
                        timestamp_str = metadata["timestamp"]
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        # Нормалізуємо timezone
                        if timestamp.tzinfo is None:
                            from datetime import timezone
                            timestamp = timestamp.replace(tzinfo=timezone.utc)
                    except:
                        continue
                    
                    if filters.get("date_from"):
                        try:
                            date_from = datetime.fromisoformat(filters["date_from"].replace('Z', '+00:00'))
                            if date_from.tzinfo is None:
                                from datetime import timezone
                                date_from = date_from.replace(tzinfo=timezone.utc)
                            if timestamp < date_from:
                                continue
                        except:
                            pass
                    
                    if filters.get("date_to"):
                        try:
                            date_to = datetime.fromisoformat(filters["date_to"].replace('Z', '+00:00'))
                            if date_to.tzinfo is None:
                                from datetime import timezone
                                date_to = date_to.replace(tzinfo=timezone.utc)
                            if timestamp > date_to:
                                continue
                        except:
                            pass
                
                # Фільтр по платформах
                if filters.get("platforms"):
                    if metadata.get("platform") not in filters["platforms"]:
                        continue
                
                filtered_ids.append(all_comments["ids"][i])
                filtered_docs.append(all_comments["documents"][i])
                filtered_metas.append(metadata)
            
            # Замінюємо на відфільтровані
            all_comments = {
                "ids": filtered_ids,
                "documents": filtered_docs,
                "metadatas": filtered_metas
            }
        
        sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        platform_distribution = defaultdict(int)
        category_counts = defaultdict(int)
        severity_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        ratings = []
        timeline_data = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        
        for metadata in all_comments["metadatas"]:
            sentiment = metadata.get("sentiment", "neutral")
            platform = metadata.get("platform", "unknown")
            category = metadata.get("category", "general")
            severity = metadata.get("severity", "medium")
            rating = metadata.get("rating", 0)
            
            # Парсимо timestamp безпечно
            try:
                timestamp_str = metadata["timestamp"]
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            sentiment_distribution[sentiment] += 1
            platform_distribution[platform] += 1
            severity_distribution[severity] += 1
            
            # Обробка категорій (може бути строкою з комами)
            if ", " in category:
                for cat in category.split(", "):
                    category_counts[cat.strip()] += 1
            else:
                category_counts[category] += 1
            
            if rating > 0:
                ratings.append(rating)
            
            # Timeline по днях
            date_key = timestamp.strftime("%Y-%m-%d")
            timeline_data[date_key][sentiment] += 1
        
        # Топ категорії
        top_categories = [
            {"category": cat, "count": count}
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Timeline список
        timeline_list = [
            {"date": date, **sentiments}
            for date, sentiments in sorted(timeline_data.items())
        ]
        
        reputation_score = self.calculate_reputation_score()
        
        return {
            "total_mentions": len(all_comments["metadatas"]),
            "sentiment_distribution": dict(sentiment_distribution),
            "platform_distribution": dict(platform_distribution),
            "severity_distribution": dict(severity_distribution),
            "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "top_categories": top_categories,
            "timeline_data": timeline_list,
            "reputation_score": reputation_score
        }
    
    def detect_crisis(self) -> Optional[CrisisAlert]:
        """Детектує кризові ситуації"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Отримуємо коментарі за останню годину
        recent_comments = db_manager.get_comments_by_timerange(hour_ago, now)
        
        if not recent_comments["metadatas"]:
            return None
        
        mentions_last_hour = len(recent_comments["metadatas"])
        
        # Розраховуємо baseline (середня кількість за годину за останні 30 днів)
        baseline = self._calculate_baseline()
        
        # Перевірка на сплеск
        is_spike = mentions_last_hour > baseline * settings.CRISIS_SPIKE_MULTIPLIER
        
        # Підрахунок негативних згадувань
        negative_count = sum(
            1 for m in recent_comments["metadatas"] 
            if m.get("sentiment") == "negative"
        )
        negative_ratio = negative_count / mentions_last_hour if mentions_last_hour > 0 else 0
        
        # Пошук критичних keywords
        critical_keywords = []
        for doc, metadata in zip(recent_comments["documents"], recent_comments["metadatas"]):
            for keyword in settings.CRISIS_CRITICAL_KEYWORDS:
                if keyword.lower() in doc.lower():
                    critical_keywords.append(keyword)
        
        critical_keywords = list(set(critical_keywords))
        
        # Визначення кризи
        is_crisis = (
            is_spike and 
            negative_ratio > settings.CRISIS_NEGATIVE_THRESHOLD and
            len(critical_keywords) > 0
        )
        
        if not is_crisis:
            return None
        
        # Визначення рівня кризи
        if negative_ratio > 0.9 and mentions_last_hour > baseline * 5:
            crisis_level = CrisisLevel.CRITICAL
        elif negative_ratio > 0.8 and mentions_last_hour > baseline * 4:
            crisis_level = CrisisLevel.HIGH
        elif negative_ratio > 0.7:
            crisis_level = CrisisLevel.MEDIUM
        else:
            crisis_level = CrisisLevel.LOW
        
        # Аналіз LLM для рекомендацій
        mentions_data = [
            {
                "body": doc,
                "sentiment": meta.get("sentiment"),
                "platform": meta.get("platform")
            }
            for doc, meta in zip(recent_comments["documents"][:20], recent_comments["metadatas"][:20])
        ]
        
        llm_analysis = openai_service.analyze_crisis_severity(mentions_data)
        
        # Визначення платформи з найбільшим негативом
        platform_negatives = defaultdict(int)
        for metadata in recent_comments["metadatas"]:
            if metadata.get("sentiment") == "negative":
                platform_negatives[metadata.get("platform")] += 1
        
        main_platform = max(platform_negatives.items(), key=lambda x: x[1])[0] if platform_negatives else None
        
        return CrisisAlert(
            crisis_level=crisis_level,
            platform=Platform(main_platform) if main_platform else None,
            description=llm_analysis.get("summary", f"Виявлено сплеск негативних згадувань: {mentions_last_hour} за годину (baseline: {baseline})"),
            affected_count=mentions_last_hour,
            critical_keywords=critical_keywords,
            timestamp=now,
            recommendations=llm_analysis.get("recommendations", [
                "Перевірити статус сервісів",
                "Підготувати офіційну заяву",
                "Активувати кризову команду"
            ])
        )
    
    def _calculate_baseline(self) -> float:
        """Розраховує базовий рівень згадувань за годину"""
        now = datetime.now()
        start = now - timedelta(days=settings.BASELINE_DAYS)
        
        all_comments = db_manager.get_comments_by_timerange(start, now)
        
        if not all_comments["metadatas"]:
            return 1.0  # Мінімальний baseline
        
        total_hours = settings.BASELINE_DAYS * 24
        mentions_per_hour = len(all_comments["metadatas"]) / total_hours
        
        return max(mentions_per_hour, 1.0)  # Мінімум 1

    def compare_brands(self, brand_names: List[str], filters: dict = None) -> List[dict]:
        """Порівняння брендів"""
        comparisons = []
        
        for brand_name in brand_names:
            # Додаємо brand_name до фільтрів
            brand_filters = filters.copy() if filters else {}
            brand_filters["brand_name"] = brand_name
            
            # Отримуємо статистику для бренду
            stats = self.get_statistics(filters=brand_filters)
            
            if stats["total_mentions"] == 0:
                continue
            
            # Аналіз сильних сторін
            strengths = []
            if stats["sentiment_distribution"]["positive"] > stats["sentiment_distribution"]["negative"]:
                strengths.append(f"Позитивний sentiment ({stats['sentiment_distribution']['positive']} відгуків)")
            
            if stats.get("average_rating") and stats["average_rating"] > 4.0:
                strengths.append(f"Високий рейтинг ({stats['average_rating']}/5)")
            
            low_severity_ratio = stats["severity_distribution"]["low"] / stats["total_mentions"]
            if low_severity_ratio > 0.6:
                strengths.append(f"Низька критичність проблем ({int(low_severity_ratio*100)}%)")
            
            # Топ платформа
            if stats.get("platform_distribution"):
                top_platform = max(stats["platform_distribution"].items(), key=lambda x: x[1])
                strengths.append(f"Активність на {top_platform[0]} ({top_platform[1]} згадувань)")
            
            # Аналіз слабких сторін
            weaknesses = []
            if stats["sentiment_distribution"]["negative"] > stats["sentiment_distribution"]["positive"]:
                weaknesses.append(f"Більше негативу ніж позитиву ({stats['sentiment_distribution']['negative']} vs {stats['sentiment_distribution']['positive']})")
            
            critical_ratio = stats["severity_distribution"]["critical"] / stats["total_mentions"]
            if critical_ratio > 0.1:
                weaknesses.append(f"Високий рівень критичних проблем ({int(critical_ratio*100)}%)")
            
            if stats.get("average_rating") and stats["average_rating"] < 3.0:
                weaknesses.append(f"Низький рейтинг ({stats['average_rating']}/5)")
            
            # Топ проблеми
            if stats.get("top_categories"):
                top_issues = stats["top_categories"][:3]
                for issue in top_issues:
                    weaknesses.append(f"Проблеми з '{issue['category']}' ({issue['count']} згадувань)")
            
            comparisons.append({
                "brand_name": brand_name,
                "total_mentions": stats["total_mentions"],
                "reputation_score": stats["reputation_score"]["overall_score"],
                "sentiment_distribution": stats["sentiment_distribution"],
                "severity_distribution": stats["severity_distribution"],
                "top_strengths": strengths[:5],
                "top_weaknesses": weaknesses[:5],
                "platform_performance": stats.get("platform_distribution", {})
            })
        
        return comparisons

    def check_negative_spike_alert(self, brand_name: str = None) -> Optional[dict]:
        """Перевірка різкого збільшення негативних згадок"""
        from datetime import timezone
        
        now = datetime.now(timezone.utc)
        two_days_ago = now - timedelta(days=settings.ALERT_CHECK_DAYS)
        four_days_ago = now - timedelta(days=settings.ALERT_CHECK_DAYS * 2)
        
        # Отримуємо коментарі за останні 2 дні
        all_recent = db_manager.get_all_comments(limit=10000)
        
        recent_comments = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }
        
        # Фільтруємо по даті та бренду
        for i, metadata in enumerate(all_recent.get("metadatas", [])):
            try:
                timestamp_str = metadata["timestamp"]
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                # Перевіряємо чи в останніх 2 днях
                if timestamp >= two_days_ago and timestamp <= now:
                    # Фільтр по бренду
                    if brand_name is None or metadata.get("brand_name") == brand_name:
                        recent_comments["ids"].append(all_recent["ids"][i])
                        recent_comments["documents"].append(all_recent["documents"][i])
                        recent_comments["metadatas"].append(metadata)
            except:
                continue
        
        if not recent_comments["metadatas"]:
            return None
        
        # Підраховуємо негатив/позитив за останні 2 дні
        recent_negative = sum(1 for m in recent_comments["metadatas"] if m.get("sentiment") == "negative")
        recent_positive = sum(1 for m in recent_comments["metadatas"] if m.get("sentiment") == "positive")
        
        # Отримуємо коментарі за попередні 2 дні (базелайн)
        baseline_comments = {
            "metadatas": []
        }
        
        # Фільтруємо за попередні 2 дні
        for metadata in all_recent.get("metadatas", []):
            try:
                timestamp_str = metadata["timestamp"]
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                # Перевіряємо чи в попередніх 2 днях
                if timestamp >= four_days_ago and timestamp < two_days_ago:
                    # Фільтр по бренду
                    if brand_name is None or metadata.get("brand_name") == brand_name:
                        baseline_comments["metadatas"].append(metadata)
            except:
                continue
        
        if not baseline_comments["metadatas"]:
            # Немає базелайну - не можемо порівняти
            return None
        
        baseline_negative = sum(1 for m in baseline_comments["metadatas"] if m.get("sentiment") == "negative")
        baseline_positive = sum(1 for m in baseline_comments["metadatas"] if m.get("sentiment") == "positive")
        
        # Розраховуємо збільшення
        if baseline_negative == 0:
            baseline_negative = 1  # Уникнення ділення на 0
        
        negative_increase_ratio = recent_negative / baseline_negative
        
        # Перевірка чи є збільшення
        if negative_increase_ratio >= settings.ALERT_NEGATIVE_INCREASE_THRESHOLD:
            # Збираємо топ проблем
            category_counts = defaultdict(int)
            for meta in recent_comments["metadatas"]:
                if meta.get("sentiment") == "negative":
                    category = meta.get("category", "general")
                    if ", " in category:
                        for cat in category.split(", "):
                            category_counts[cat.strip()] += 1
                    else:
                        category_counts[category] += 1
            
            top_issues = [
                {"category": cat, "count": count}
                for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            ][:5]
            
            # Генеруємо AI summary
            negative_comments = [
                {"body": doc, "sentiment": meta.get("sentiment"), "platform": meta.get("platform")}
                for doc, meta in zip(recent_comments["documents"], recent_comments["metadatas"])
                if meta.get("sentiment") == "negative"
            ][:20]
            
            ai_analysis = openai_service.analyze_negative_spike(negative_comments, negative_increase_ratio)
            
            return {
                "brand_name": brand_name or "All brands",
                "negative_count": recent_negative,
                "positive_count": recent_positive,
                "total_mentions": len(recent_comments["metadatas"]),
                "increase_ratio": negative_increase_ratio,
                "baseline_negative": baseline_negative,
                "ai_summary": ai_analysis.get("summary", "Збільшення негативних згадок"),
                "top_issues": top_issues,
                "recommendations": ai_analysis.get("recommendations", [])
            }
        
        return None


# Singleton
analytics_service = AnalyticsService()
