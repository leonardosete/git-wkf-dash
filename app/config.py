# config.py
import os  # ✅ necessário para usar os.getenv
os.environ['TZ'] = 'America/Sao_Paulo'
import time
time.tzset()

# GitHub API token via variável de ambiente
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("⚠️  Atenção: GITHUB_TOKEN não foi encontrado no ambiente.")

# Default repositories to monitor
DEFAULT_REPOS = [
    "leonardosete/kind-cluster-n8n",
    "leonardosete/teste-ricardinho-origem",
    "leonardosete/git-wkf-dash",
    "leonardosete/teste-workflow"
]

# Status color mapping
STATUS_COLORS = {
    "success": "#28a745",
    "failure": "#dc3545",
    "cancelled": "#6c757d",
    "skipped": "#ffc107",
    "in_progress": "#17a2b8"
}
