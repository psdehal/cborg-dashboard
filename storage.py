"""Local data storage for CBORG dashboard, indexed by API key."""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class CBORGStorage:
    """Handles local storage of CBORG data indexed by API key."""

    def __init__(self, data_dir: str = ".cborg_data"):
        """Initialize storage with specified data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def _get_key_hash(self, api_key: str) -> str:
        """Generate a hash of the API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    def _get_data_file(self, api_key: str) -> Path:
        """Get the data file path for a specific API key."""
        key_hash = self._get_key_hash(api_key)
        return self.data_dir / f"{key_hash}.json"

    def load_data(self, api_key: str) -> Dict:
        """Load data for a specific API key."""
        data_file = self._get_data_file(api_key)

        if not data_file.exists():
            return self._create_empty_data(api_key)

        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._create_empty_data(api_key)

    def save_data(self, api_key: str, data: Dict) -> None:
        """Save data for a specific API key."""
        data_file = self._get_data_file(api_key)
        data['last_updated'] = datetime.now().isoformat()

        with open(data_file, 'w') as f:
            json.dump(data, indent=2, fp=f)

    def _create_empty_data(self, api_key: str) -> Dict:
        """Create empty data structure for a new API key."""
        return {
            'api_key_preview': f"{api_key[:8]}...{api_key[-4:]}",
            'first_seen': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'models': {
                'last_check': None,
                'known_models': [],
                'new_models': []
            },
            'spend': {
                'last_check': None,
                'history': []
            }
        }

    def update_models(self, api_key: str, current_models: List[str]) -> Dict:
        """
        Update model list and identify new models.

        Returns dict with:
        - new_models: list of newly discovered models
        - all_models: complete current list
        """
        data = self.load_data(api_key)

        previous_models = set(data['models']['known_models'])
        current_models_set = set(current_models)

        # Find new models
        new_models = list(current_models_set - previous_models)

        # Update stored data
        data['models']['last_check'] = datetime.now().isoformat()
        data['models']['known_models'] = sorted(current_models)
        data['models']['new_models'] = new_models

        self.save_data(api_key, data)

        return {
            'new_models': new_models,
            'all_models': sorted(current_models),
            'total_count': len(current_models)
        }

    def add_spend_record(self, api_key: str, spend_info: Dict) -> None:
        """
        Add a spend record to history if spend has changed since last record.

        Only creates a new record if current_spend differs from the last recorded value.
        This prevents duplicate entries when running dashboard multiple times without usage.
        """
        data = self.load_data(api_key)

        current_spend = spend_info.get('current_spend')

        # Check if we should add a new record
        should_add = True
        history = data['spend']['history']

        if history and current_spend is not None:
            last_record = history[-1]
            last_spend = last_record.get('current_spend')

            # Only add if spend changed
            if last_spend == current_spend:
                should_add = False

        if should_add and current_spend is not None:
            spend_record = {
                'timestamp': datetime.now().isoformat(),
                'current_spend': spend_info.get('current_spend'),
                'budget_limit': spend_info.get('budget_limit'),
                'remaining': spend_info.get('remaining'),
                'key_alias': spend_info.get('key_alias')
            }

            data['spend']['history'].append(spend_record)

            # Keep only last 365 records (roughly 1 year of daily checks)
            data['spend']['history'] = data['spend']['history'][-365:]

        data['spend']['last_check'] = datetime.now().isoformat()
        self.save_data(api_key, data)

    def get_last_check(self, api_key: str) -> Optional[str]:
        """Get the timestamp of the last check."""
        data = self.load_data(api_key)
        return data['models']['last_check']

    def list_tracked_keys(self) -> List[Dict]:
        """List all tracked API keys with summary info."""
        keys = []

        for data_file in self.data_dir.glob("*.json"):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    keys.append({
                        'preview': data.get('api_key_preview', 'Unknown'),
                        'first_seen': data.get('first_seen'),
                        'last_updated': data.get('last_updated'),
                        'model_count': len(data.get('models', {}).get('known_models', []))
                    })
            except (json.JSONDecodeError, IOError):
                continue

        return sorted(keys, key=lambda x: x['last_updated'], reverse=True)
