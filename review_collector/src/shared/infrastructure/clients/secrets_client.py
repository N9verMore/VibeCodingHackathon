"""
Secrets Manager Client

Wrapper for AWS Secrets Manager to retrieve API credentials.
"""

import os
import json
import logging
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class SecretsClient:
    """
    AWS Secrets Manager client for retrieving API credentials.
    
    Expected secret structure:
    {
        "serpapi": {
            "api_key": "your_serpapi_api_key"
        },
        "appstore": {
            "key_id": "...",
            "issuer_id": "...",
            "private_key": "..."
        },
        "googleplay": {
            "type": "service_account",
            "project_id": "...",
            "private_key": "..."
        },
        "trustpilot": {
            "api_key": "..."
        }
    }
    """
    
    def __init__(self, secret_name: str = None):
        """
        Initialize secrets client.
        
        Args:
            secret_name: Secret name in Secrets Manager (defaults to env var)
        """
        self.secret_name = secret_name or os.environ.get(
            'SECRET_NAME',
            'review-collector/credentials'
        )
        self.client = boto3.client('secretsmanager')
        self._cache: Dict[str, Any] = {}
        logger.info(f"Initialized SecretsClient for secret: {self.secret_name}")
    
    def get_all_credentials(self) -> Dict[str, Any]:
        """
        Get all API credentials from secret.
        
        Returns:
            Dictionary with all credentials
        """
        if self._cache:
            return self._cache
        
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secret_string = response['SecretString']
            credentials = json.loads(secret_string)
            
            self._cache = credentials
            logger.info(f"Retrieved credentials for: {list(credentials.keys())}")
            return credentials
        
        except ClientError as e:
            logger.error(f"Failed to retrieve secret {self.secret_name}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse secret JSON: {e}")
            raise
    
    def get_appstore_credentials(self) -> Dict[str, str]:
        """
        Get App Store Connect API credentials.
        
        Returns:
            Dict with key_id, issuer_id, private_key
        """
        credentials = self.get_all_credentials()
        
        if 'appstore' not in credentials:
            raise ValueError("App Store credentials not found in secret")
        
        appstore = credentials['appstore']
        required_keys = ['key_id', 'issuer_id', 'private_key']
        
        for key in required_keys:
            if key not in appstore:
                raise ValueError(f"Missing required App Store credential: {key}")
        
        return appstore
    
    def get_googleplay_credentials(self) -> Dict[str, str]:
        """
        Get Google Play API credentials (service account).
        
        Returns:
            Dict with service account credentials
        """
        credentials = self.get_all_credentials()
        
        if 'googleplay' not in credentials:
            raise ValueError("Google Play credentials not found in secret")
        
        googleplay = credentials['googleplay']
        required_keys = ['type', 'project_id', 'private_key']
        
        for key in required_keys:
            if key not in googleplay:
                raise ValueError(f"Missing required Google Play credential: {key}")
        
        return googleplay
    
    def get_trustpilot_credentials(self) -> Dict[str, str]:
        """
        Get Trustpilot API credentials.
        
        Returns:
            Dict with api_key
        """
        credentials = self.get_all_credentials()
        
        if 'trustpilot' not in credentials:
            raise ValueError("Trustpilot credentials not found in secret")
        
        trustpilot = credentials['trustpilot']
        
        if 'api_key' not in trustpilot:
            raise ValueError("Missing required Trustpilot credential: api_key")
        
        return trustpilot
    
    def get_serpapi_key(self) -> str:
        """
        Get SerpAPI key.
        
        Returns:
            SerpAPI API key string
        """
        credentials = self.get_all_credentials()
        
        if 'serpapi' not in credentials:
            raise ValueError("SerpAPI credentials not found in secret")
        
        serpapi = credentials['serpapi']
        
        if 'api_key' not in serpapi:
            raise ValueError("Missing required SerpAPI credential: api_key")
        
        return serpapi['api_key']

