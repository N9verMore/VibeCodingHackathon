"""
DataForSEO Trustpilot Client

Fetches reviews from Trustpilot using DataForSEO API.
This API uses an async task-based approach:
1. Create task (task_post)
2. Check readiness (tasks_ready)
3. Get results (task_get)

DataForSEO Docs: https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/
"""

import logging
import time
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import from Lambda Layer (located in /opt/python/)
from infrastructure.clients.base_api_client import BaseAPIClient
from domain.review import Review, ReviewSource


logger = logging.getLogger(__name__)


class DataForSEOTrustpilotClient(BaseAPIClient):
    """
    Trustpilot review collector using DataForSEO API.
    
    Uses async task workflow:
    1. POST task to collect reviews
    2. Poll for task completion
    3. GET results when ready
    
    Example identifiers:
    - Tesla: "www.tesla.com"
    - Amazon: "www.amazon.com"
    - Zara: "www.zara.com"
    """
    
    BASE_URL = "https://api.dataforseo.com/v3/business_data/trustpilot/reviews"
    
    def __init__(
        self,
        login: str,
        password: str,
        timeout: int = 30,
        max_poll_attempts: int = 15,
        poll_interval: int = 1
    ):
        """
        Initialize DataForSEO client.
        
        Args:
            login: DataForSEO login (email)
            password: DataForSEO password
            timeout: Request timeout in seconds
            max_poll_attempts: Maximum number of polling attempts (15 attempts)
            poll_interval: Seconds between polling attempts (1 second for faster response)
        """
        super().__init__(timeout)
        self.login = login
        self.password = password
        self.max_poll_attempts = max_poll_attempts
        self.poll_interval = poll_interval
        
        if not self.login or not self.password:
            raise ValueError("DataForSEO login and password are required")
        
        # Setup Basic Auth
        self._setup_auth()
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def _setup_auth(self):
        """Setup Basic Authentication header"""
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {encoded}"
        
        # Add auth header to session
        self.session.headers.update({
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        })
        
        logger.info("✅ DataForSEO authentication configured")
    
    def authenticate(self, credentials: Dict[str, str]) -> None:
        """
        No-op for DataForSEO (credentials passed in constructor).
        Kept for interface compatibility.
        """
        pass
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from Trustpilot via DataForSEO API.
        
        Workflow:
        1. Create task to collect reviews
        2. Wait for task completion
        3. Fetch and parse results
        
        Args:
            app_identifier: Domain name (e.g. "www.zara.com")
            since: Not supported by DataForSEO (ignored)
            limit: Maximum number of reviews (depth parameter, max: 5000)
            brand: Brand identifier for tracking
            
        Returns:
            List of normalized Review entities
        """
        logger.info(f"🔍 Fetching Trustpilot reviews for domain={app_identifier}")
        
        if since:
            logger.warning("'since' parameter not supported by DataForSEO - ignored")
        
        limit = limit or 100
        # DataForSEO recommends depth in multiples of 20 (processes 20 reviews per SERP)
        # Max: 25000, but we limit to 5000 for safety
        depth = min(limit, 5000)
        # Round up to nearest multiple of 20 for optimal billing
        depth = ((depth + 19) // 20) * 20
        
        try:
            # Step 1: Create task
            task_id = self._create_task(app_identifier, depth)
            logger.info(f"✅ Task created: {task_id}")
            
            # Step 2: Wait for task completion
            self._wait_for_task(task_id)
            logger.info(f"✅ Task completed: {task_id}")
            
            # Step 3: Get results
            results = self._get_results(task_id)
            logger.info(f"✅ Results retrieved: {len(results)} reviews")
            
            # Step 4: Normalize reviews
            reviews = []
            for item in results:
                try:
                    review = self._normalize_review(item, brand, app_identifier)
                    reviews.append(review)
                except Exception as e:
                    logger.error(f"Failed to normalize review: {e}")
                    logger.debug(f"Raw review data: {item}")
                    continue
            
            logger.info(f"✅ Successfully parsed {len(reviews)} Trustpilot reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch Trustpilot reviews: {e}")
            raise
    
    def _create_task(self, domain: str, depth: int) -> str:
        """
        Create review collection task.
        
        According to DataForSEO docs:
        - depth should be in multiples of 20 (system processes 20 reviews per SERP)
        - max depth: 25000
        - billing: per each SERP containing up to 20 results
        
        Args:
            domain: Trustpilot domain (e.g. "www.zara.com")
            depth: Number of reviews to collect (should be multiple of 20)
            
        Returns:
            Task ID for polling
        """
        url = f"{self.BASE_URL}/task_post"
        
        payload = [{
            "domain": domain,
            "depth": depth,
            "sort_by": "recency",  # Most recent reviews first
            "priority": 1,  # Normal priority (1-2)
            "tag": f"trustpilot_{domain}"
        }]
        
        logger.info(f"📤 Creating task for domain={domain}, depth={depth}")
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract task_id from response
            # Response structure: {"tasks": [{"id": "...", "status_code": 20100, ...}]}
            if not data.get('tasks') or len(data['tasks']) == 0:
                raise ValueError("No tasks in response")
            
            task = data['tasks'][0]
            task_id = task.get('id')
            status_code = task.get('status_code')
            
            if not task_id:
                raise ValueError(f"No task_id in response: {task}")
            
            if status_code != 20100:
                status_message = task.get('status_message', 'Unknown error')
                raise ValueError(f"Task creation failed: {status_message} (code: {status_code})")
            
            logger.info(f"✅ Task created successfully: {task_id}")
            return task_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise
    
    def _wait_for_task(self, task_id: str) -> None:
        """
        Poll API until task is ready.
        
        According to DataForSEO docs, tasks_ready returns:
        {
          "tasks": [
            {
              "id": "parent_id",
              "result": [
                {"id": "task_id", "endpoint": "..."}
              ]
            }
          ]
        }
        
        Args:
            task_id: Task ID to check
            
        Raises:
            TimeoutError: If task doesn't complete within max_poll_attempts
        """
        url = f"{self.BASE_URL}/tasks_ready"
        
        logger.info(f"⏳ Waiting for task {task_id} to complete...")
        
        for attempt in range(self.max_poll_attempts):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # Check if our task is in ready tasks
                # According to docs: tasks[].result[] contains completed task IDs
                tasks = data.get('tasks', [])
                for task in tasks:
                    result = task.get('result', [])
                    for ready_task in result:
                        if ready_task.get('id') == task_id:
                            logger.info(f"✅ Task {task_id} is ready!")
                            return
                
                # Task not ready yet, wait and retry
                logger.debug(f"Task not ready yet, attempt {attempt + 1}/{self.max_poll_attempts}")
                time.sleep(self.poll_interval)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Polling attempt {attempt + 1} failed: {e}")
                time.sleep(self.poll_interval)
        
        raise TimeoutError(
            f"Task {task_id} did not complete within "
            f"{self.max_poll_attempts * self.poll_interval} seconds"
        )
    
    def _get_results(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve results for completed task.
        
        Args:
            task_id: Completed task ID
            
        Returns:
            List of review items
        """
        url = f"{self.BASE_URL}/task_get/{task_id}"
        
        logger.info(f"📥 Retrieving results for task {task_id}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extract reviews from response
            # Response structure: {"tasks": [{"result": [{"items": [...]}]}]}
            tasks = data.get('tasks', [])
            if not tasks:
                logger.warning("No tasks in response")
                return []
            
            task = tasks[0]
            results = task.get('result', [])
            if not results:
                logger.warning("No results in task")
                return []
            
            result = results[0]
            items = result.get('items', [])
            
            logger.info(f"✅ Retrieved {len(items)} reviews")
            return items
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to get results: {e}")
            raise
    
    def _normalize_review(
        self,
        raw_data: Dict[str, Any],
        brand: str,
        app_identifier: str
    ) -> Review:
        """
        Normalize DataForSEO Trustpilot review to Review entity.
        
        DataForSEO response structure (according to official docs):
        https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/task_get/
        
        {
            "type": "trustpilot_review_search",
            "rank_group": 1,
            "rank_absolute": 1,
            "position": "right",
            "url": "https://www.trustpilot.com/reviews/...",
            "rating": {
                "rating_type": "Max5",
                "value": 5,
                "votes_count": 0,
                "rating_max": 5
            },
            "verified": true,
            "language": "en",
            "timestamp": "2019-11-15 12:57:46 +00:00",
            "title": "Excellent service",
            "review_text": "I had a great experience...",
            "review_images": null,
            "user_profile": {
                "name": "John D.",
                "url": "https://www.trustpilot.com/users/...",
                "image_url": "https://...",
                "location": "US",
                "reviews_count": 5
            },
            "responses": []
        }
        """
        # Extract fields with safe defaults
        rating_data = raw_data.get('rating', {})
        rating = int(rating_data.get('value', 0)) if isinstance(rating_data, dict) else 0
        
        title = raw_data.get('title', '')
        text = raw_data.get('review_text', '')
        date_str = raw_data.get('timestamp', '')  # FIXED: was 'publication_date'
        url = raw_data.get('url', '')
        language = raw_data.get('language', 'en')  # FIXED: now using actual language from API
        verified = raw_data.get('verified', False)
        
        # Extract author info from user_profile (FIXED: was 'author')
        user_profile = raw_data.get('user_profile', {})
        if isinstance(user_profile, dict):
            author = user_profile.get('name', '')
            country = user_profile.get('location', '')  # FIXED: now extracting location
        else:
            author = ''
            country = ''
        
        # Generate unique ID (DataForSEO doesn't provide stable review IDs)
        import hashlib
        id_content = f"{app_identifier}_{author}_{title}_{date_str}"
        review_id = hashlib.md5(id_content.encode()).hexdigest()
        
        # Parse date
        try:
            # DataForSEO format: "2019-11-15 12:57:46 +00:00"
            # Remove timezone for simplicity
            date_clean = date_str.split('+')[0].strip()
            created_at = datetime.strptime(date_clean, "%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            created_at = datetime.utcnow()
        
        # Use review URL or generate backlink
        backlink = url or f"https://www.trustpilot.com/review/{app_identifier}"
        
        return Review(
            id=review_id,
            source=ReviewSource.TRUSTPILOT,
            backlink=backlink,
            brand=brand,
            app_identifier=app_identifier,
            title=title or None,
            text=text or None,
            rating=rating,
            language=language,  # FIXED: now using actual language from API
            country=country or None,  # FIXED: now using location from user_profile
            author_hint=author or None,
            created_at=created_at,
            fetched_at=datetime.utcnow()
        )

