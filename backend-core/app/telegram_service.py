import requests
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Відправити повідомлення в Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot not configured. Skipping notification.")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_alert(self, alert_data: dict) -> bool:
        """Відправити алерт про негативні згадки"""
        
        brand = alert_data.get("brand_name", "Unknown")
        negative_count = alert_data.get("negative_count", 0)
        positive_count = alert_data.get("positive_count", 0)
        total_mentions = alert_data.get("total_mentions", 0)
        increase_ratio = alert_data.get("increase_ratio", 0)
        ai_summary = alert_data.get("ai_summary", "")
        top_issues = alert_data.get("top_issues", [])
        
        # Формуємо повідомлення
        message = f"""
🚨 *ALERT: Збільшення негативних згадок*

📱 *Бренд:* {brand}
📊 *Період:* Останні 2 дні

*Статистика:*
• Всього згадувань: {total_mentions}
• ❌ Негативні: {negative_count}
• ✅ Позитивні: {positive_count}
• 📈 Зростання негативу: {increase_ratio:.1f}x

*🤖 AI Аналіз:*
{ai_summary}

*⚠️ Топ проблеми:*
"""
        
        for i, issue in enumerate(top_issues[:5], 1):
            message += f"{i}. {issue.get('category', 'Unknown')}: {issue.get('count', 0)} згадувань\n"
        
        message += f"\n🔗 Перевірити деталі в dashboard"
        
        return self.send_message(message)


# Singleton
telegram_service = TelegramService()
