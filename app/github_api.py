# github_api.py
import requests
from datetime import datetime, timedelta
import time

class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.rate_limit_remaining = 5000

    def _make_request(self, endpoint, params=None):
        """Make a GET request to the GitHub API with rate limit handling"""
        if self.rate_limit_remaining <= 1:
            time.sleep(60)  # Wait for rate limit reset
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise ValueError(f"Resource not found: {endpoint}")
        else:
            raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    def get_workflow_runs(self, repo, per_page=100):
        """Fetch workflow runs for a repository"""
        endpoint = f"repos/{repo}/actions/runs"
        params = {"per_page": per_page}
        
        try:
            response = self._make_request(endpoint, params)
            runs = response.get("workflow_runs", [])
            
            # Transform the data
            processed_runs = []
            for run in runs:
                processed_run = {
                    "id": run["id"],
                    "repository": repo,
                    "workflow_name": run["name"],
                    "status": run["status"],
                    "conclusion": run["conclusion"],
                    "started_at": run["run_started_at"],
                    "updated_at": run["updated_at"],
                    "html_url": run["html_url"],
                    "branch": run["head_branch"]
                }
                processed_runs.append(processed_run)
            
            return processed_runs
            
        except Exception as e:
            raise Exception(f"Error fetching workflow runs for {repo}: {str(e)}")