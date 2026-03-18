"""
Parser for extracting data from Kickstarter HTML.
"""
import json
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_project_data(url: str) -> dict:
    """
    Extracts project metadata from the embedded __NEXT_DATA__ JSON script.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    try:
        logger.info(f"Fetching {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if not script_tag:
            logger.warning(f"No __NEXT_DATA__ found for {url}")
            return None
            
        data = json.loads(script_tag.string)
        project_data = data.get('props', {}).get('pageProps', {}).get('project', {})
        if not project_data:
            apollo_state = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
            for key, val in apollo_state.items():
                if key.startswith('Project:'):
                    project_data = val
                    break
                    
        if not project_data:
            logger.warning(f"Could not find project payload in __NEXT_DATA__ for {url}")
            return None
            
        name = project_data.get('name', 'Unknown')
        goal = project_data.get('goal', {}).get('amount', project_data.get('goal', 0))
        pledged = project_data.get('pledged', {}).get('amount', project_data.get('pledged', 0))
        
        category = "Unknown"
        cat_ref = project_data.get('category')
        if isinstance(cat_ref, dict):
            category = cat_ref.get('name', "Unknown")
        elif isinstance(cat_ref, str):
            category = cat_ref
            
        currency = project_data.get('currency', 'USD')
        deadline = project_data.get('deadlineAt') or project_data.get('stateChangedAt')
        launched_at = project_data.get('launchedAt')
        state = project_data.get('state', 'Unknown')
        
        # Format timestamps correctly to standard string (YYYY-MM-DD HH:MM:SS) if they are integers/timestamps
        if isinstance(deadline, (int, float)):
            deadline = datetime.fromtimestamp(deadline).strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(launched_at, (int, float)):
            launched_at = datetime.fromtimestamp(launched_at).strftime('%Y-%m-%d %H:%M:%S')
        
        # Adding some missing fields required by the model: backers, country, subcategory
        # The model uses: project_id, name, category, subcategory, country, currency, goal, launched_at, deadline, pledged, backers, state
        backers = project_data.get('backersCount', 0)
        country = project_data.get('country', 'US')
        subcategory = "Unknown" # Often nested in category or tags
        
        return {
            'project_id': project_data.get('id', hash(url)),
            'name': name,
            'category': category,
            'subcategory': subcategory,
            'country': country,
            'currency': currency,
            'goal': float(goal) if goal else 0.0,
            'launched_at': launched_at,
            'deadline': deadline,
            'pledged': float(pledged) if pledged else 0.0,
            'backers': int(backers),
            'state': str(state).lower(),
            'url': url
        }
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None
