from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from espn_client import get_league, get_standings, get_scoreboard, get_free_agents
from csv_loader import StatsLoader

app = FastAPI(title="League Site (FastAPI)")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
stats_loader = StatsLoader(csv_dir="data")


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


@app.get("/teams", response_class=HTMLResponse)
async def teams_view(request: Request):
    league = get_league()
    teams = league.teams
    return templates.TemplateResponse(
        "teams.html", {"request": request, "teams": teams}
    )


@app.get("/waivers", response_class=HTMLResponse)
async def waivers_view(request: Request, pos: str | None = None):
    players = get_free_agents(position=pos)
    return templates.TemplateResponse(
        "waivers.html", {"request": request, "players": players, "pos": pos or "ALL"}
    )


@app.get("/team/{team_name}", response_class=HTMLResponse)
async def team_view(request: Request, team_name: str, weeks: int | None = None):
    stats = stats_loader.get_team_stats(team_name, weeks=weeks)
    return templates.TemplateResponse(
        "team.html", {"request": request, "team_name": team_name, "stats": stats}
    )
