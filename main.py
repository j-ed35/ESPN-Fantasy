from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from espn_client import get_league, get_standings, get_scoreboard, get_free_agents

app = FastAPI(title="League Site (FastAPI)")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    league = get_league()
    return templates.TemplateResponse(
        "index.html", {"request": request, "league": league.settings.name}
    )


@app.get("/standings", response_class=HTMLResponse)
async def standings_view(request: Request):
    rows = get_standings()
    return templates.TemplateResponse(
        "standings.html", {"request": request, "rows": rows}
    )


@app.get("/matchups", response_class=HTMLResponse)
async def matchups_view(request: Request):
    matchups = get_scoreboard()
    return templates.TemplateResponse(
        "matchups.html", {"request": request, "matchups": matchups}
    )


@app.get("/waivers", response_class=HTMLResponse)
async def waivers_view(request: Request, pos: str | None = None):
    players = get_free_agents(position=pos)
    return templates.TemplateResponse(
        "waivers.html", {"request": request, "players": players, "pos": pos or "ALL"}
    )
