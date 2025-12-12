"""CBORG API client."""

import requests
from typing import List, Dict, Optional
from openai import OpenAI


class CBORGClient:
    """Client for interacting with CBORG API."""

    def __init__(self, api_key: str, base_url: str = "https://api.cborg.lbl.gov"):
        """Initialize CBORG client."""
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=f"{base_url}/v1")

    def get_models(self) -> List[str]:
        """
        Get list of all available models.

        Returns:
            List of model IDs
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            raise Exception(f"Failed to fetch models: {e}")

    def get_key_info(self) -> Optional[Dict]:
        """
        Get API key information including spend and budget.

        Returns:
            Key info dict or None if not available
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/key/info", headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            return None

    def get_spend_info(self) -> Optional[Dict]:
        """
        Get spending information.

        Returns:
            Spend info dict with current_spend, budget_limit, remaining, etc.
            None if not available
        """
        key_info = self.get_key_info()

        if key_info and 'info' in key_info:
            info = key_info['info']
            current_spend = info.get('spend', 0)
            budget_limit = info.get('max_budget')

            return {
                'current_spend': current_spend,
                'budget_limit': budget_limit,
                'remaining': budget_limit - current_spend if budget_limit else None,
                'reset_date': info.get('budget_reset_at'),
                'key_alias': info.get('key_alias'),
                'created_at': info.get('created_at'),
                'model_spend': info.get('model_spend', {})
            }

        return None

    def test_connection(self) -> bool:
        """
        Test if the API connection is working.

        Returns:
            True if connection successful
        """
        try:
            models = self.get_models()
            return len(models) > 0
        except Exception:
            return False
