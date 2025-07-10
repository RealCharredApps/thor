"""
THOR Client Module
Provides interface for interacting with THOR AI assistant
"""

import json
import requests
from typing import Dict, Any, Optional

class ThorClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """Initialize THOR client
        
        Args:
            base_url: Base URL for THOR API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
            
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send a query to THOR
        
        Args:
            prompt: The user prompt/question
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict containing THOR's response
        """
        endpoint = f"{self.base_url}/query"
        payload = {
            "prompt": prompt,
            **kwargs
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ThorClientError(f"Error querying THOR: {str(e)}")

    def get_tools(self) -> Dict[str, Any]:
        """Get list of available THOR tools
        
        Returns:
            Dict containing tool definitions
        """
        endpoint = f"{self.base_url}/tools"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ThorClientError(f"Error getting tools: {str(e)}")

class ThorClientError(Exception):
    """Custom exception for THOR client errors"""
    pass

# Example usage
if __name__ == "__main__":
    # Create client instance
    client = ThorClient(api_key="your-api-key")
    
    # Send a query
    try:
        response = client.query("What tools are available?")
        print(json.dumps(response, indent=2))
    except ThorClientError as e:
        print(f"Error: {e}")