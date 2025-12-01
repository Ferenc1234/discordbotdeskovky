"""
API Client for zatrolene-hry.cz
Provides async methods to interact with the board games API
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional


class ZatroleneHryClient:
    """Client for interacting with zatrolene-hry.cz API"""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make an HTTP request to the API
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary or None if request fails
        """
        await self._ensure_session()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    print(f"API request failed: {response.status} - {url}")
                    return None
        except asyncio.TimeoutError:
            print(f"API request timeout: {url}")
            return None
        except aiohttp.ClientError as e:
            print(f"API request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during API request: {e}")
            return None
    
    async def search_games(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for board games
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of game dictionaries
        """
        params = {
            'query': query,
            'limit': limit
        }
        
        # Try different possible endpoints
        endpoints = ['games/search', 'search', 'games']
        
        for endpoint in endpoints:
            result = await self._make_request(endpoint, params=params)
            if result:
                # Handle different response formats
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict):
                    # Check common keys for game lists
                    for key in ['games', 'data', 'results', 'items']:
                        if key in result and isinstance(result[key], list):
                            return result[key]
                    # If result is a single game, wrap it in a list
                    return [result]
        
        # Return empty list if no endpoint worked
        print(f"No results found for query: {query}")
        return []
    
    async def get_game_details(self, game_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific game
        
        Args:
            game_id: ID of the game
            
        Returns:
            Game details dictionary or None if not found
        """
        # Try different possible endpoints
        endpoints = [f'games/{game_id}', f'game/{game_id}']
        
        for endpoint in endpoints:
            result = await self._make_request(endpoint)
            if result:
                # If result is wrapped, try to unwrap it
                if isinstance(result, dict):
                    if 'game' in result:
                        return result['game']
                    elif 'data' in result:
                        return result['data']
                    return result
        
        return None
    
    async def get_categories(self) -> List[Dict]:
        """
        Get list of game categories
        
        Returns:
            List of category dictionaries
        """
        # Try different possible endpoints
        endpoints = ['categories', 'game-categories', 'genres']
        
        for endpoint in endpoints:
            result = await self._make_request(endpoint)
            if result:
                # Handle different response formats
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict):
                    # Check common keys for category lists
                    for key in ['categories', 'data', 'results', 'items']:
                        if key in result and isinstance(result[key], list):
                            return result[key]
        
        return []
    
    async def get_games_by_category(
        self,
        category_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get games filtered by category
        
        Args:
            category_id: Category ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of game dictionaries
        """
        params = {'limit': limit}
        endpoints = [
            f'categories/{category_id}/games',
            f'games?category={category_id}'
        ]
        
        for endpoint in endpoints:
            result = await self._make_request(endpoint, params=params)
            if result:
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict):
                    for key in ['games', 'data', 'results', 'items']:
                        if key in result and isinstance(result[key], list):
                            return result[key]
        
        return []
    
    async def get_popular_games(self, limit: int = 10) -> List[Dict]:
        """
        Get popular/trending games
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of game dictionaries
        """
        params = {'limit': limit}
        endpoints = ['games/popular', 'games/trending', 'games']
        
        for endpoint in endpoints:
            result = await self._make_request(endpoint, params=params)
            if result:
                if isinstance(result, list):
                    return result[:limit]
                elif isinstance(result, dict):
                    for key in ['games', 'data', 'results', 'items']:
                        if key in result and isinstance(result[key], list):
                            return result[key][:limit]
        
        return []
    
    async def close(self):
        """Close the API client session. Should be called when done using the client."""
        await self._close_session()
