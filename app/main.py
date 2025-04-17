from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from collections import defaultdict
import os, httpx, redis, logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")

logging.basicConfig(filename="workflows.log", level=logging.INFO, format="%(asctime)s - %(message)s")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOS = os.getenv("REPOS", "").split(",")

WEBHOOK_URL = os.getenv("WH_URL", "https://n8n-test.devops-master.shop/webhook/messages-upsert")
WH_PHONE = os.getenv("WH_PHONE", "5511952520474")
WH_INSTANCE = os.getenv("WH_INSTANCE", "leosetecel")  # 👈 define aqui o nome da instância evolution-api

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
try:
    redis_client.ping()
except redis.exceptions.ConnectionError:
    raise RuntimeError("❌ Redis não está acessível.")

@app.get("/health")
def health_check():
    try:
        redis_client.ping()
        return JSONResponse({"status": "ok", "redis": "connected", "repos": len(REPOS)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/workflows", response_class=HTMLResponse)
async def get_workflows(request: Request, repo: str = Query(default="", alias="repo"), status: str = Query(default="")):
    grouped = defaultdict(lambda: {"items": [], "counts": {"success": 0, "failure": 0, "in_progress": 0}})
    in_progress_list = []
    total_runs = total_success = total_failure = 0
    failure_ranking = []

    async with httpx.AsyncClient() as client:
        for r in REPOS:
            if repo and repo != r:
                continue
            url = f"https://api.github.com/repos/{r}/actions/runs?per_page=10"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                continue
            runs = resp.json().get("workflow_runs", [])
            for run in runs:
                run_id = str(run["id"])
                s = run["status"]
                c = run["conclusion"]

                # determinar display_status
                if s == "in_progress":
                    display_status = "in_progress"
                elif s == "completed":
                    display_status = c if c else "other"
                else:
                    display_status = "queued"

                if status:
                    if status == "in_progress" and s != "in_progress":
                        continue
                    elif status in ["success", "failure"] and c != status:
                        continue

                grouped[r]["items"].append({
                    "workflow": run["name"],
                    "status": display_status,
                    "conclusion": c,
                    "created_at": run["created_at"],
                    "html_url": run["html_url"]
                })

                if display_status == "success":
                    grouped[r]["counts"]["success"] += 1
                elif display_status == "failure":
                    grouped[r]["counts"]["failure"] += 1
                elif display_status == "in_progress":
                    grouped[r]["counts"]["in_progress"] += 1

                if s == "in_progress":
                    in_progress_list.append({
                        "workflow": run["name"],
                        "repo": r,
                        "status": s,
                        "created_at": run["created_at"],
                        "html_url": run["html_url"],
                    })

                    redis_key = f"workflow:pending:{run_id}"
                    if not redis_client.get(redis_key):
                        redis_client.setex(redis_key, 86400, "1")
                        await client.post(WEBHOOK_URL, json={
                            "phone": WH_PHONE,
                            "message": f"🛠 *Workflow Iniciado!*\n📦 `{r}`\n⚙️ {run['name']}\n⏱ *Status:* {s}\n🔗 {run['html_url']}",
                            "instance": WH_INSTANCE
                        })

                elif s == "completed":
                    redis_key = f"workflow:pending:{run_id}"
                    if redis_client.get(redis_key):
                        emoji = "✅" if c == "success" else "❌" if c == "failure" else "🔁"
                        title = "*Workflow Finalizado com Sucesso!*" if c == "success" else "*Workflow Falhou!*" if c == "failure" else "*Workflow Finalizado*"
                        await client.post(WEBHOOK_URL, json={
                            "phone": WH_PHONE,
                            "message": f"{emoji} {title}\n📦 `{r}`\n⚙️ {run['name']}\n📊 *Conclusão:* {c or 'N/A'}\n🔗 {run['html_url']}",
                            "instance": WH_INSTANCE
                        })
                        redis_client.delete(redis_key)

    for repo, data in grouped.items():
        c = data["counts"]
        total_success += c.get("success", 0)
        total_failure += c.get("failure", 0)
        total_runs += sum(c.values())
        if c.get("failure", 0) > 0:
            failure_ranking.append((repo, c.get("failure", 0)))

    top_failures = [r for r, _ in sorted(failure_ranking, key=lambda x: x[1], reverse=True)[:3]]

    # ✅ Remove repositórios sem workflows válidos
    grouped = {repo: data for repo, data in grouped.items() if data["items"]}

    return templates.TemplateResponse("partials/workflows.html", {
        "request": request,
        "repos": REPOS,
        "selected_repo": repo,
        "selected_status": status,
        "grouped": grouped,
        "in_progress": in_progress_list,
        "total_runs": total_runs,
        "total_success": total_success,
        "total_failure": total_failure,
        "total_in_progress": len(in_progress_list),
        "top_failures": top_failures
    })