import os
from dotenv import load_dotenv
from espn_api.football import League
from services.cache import cached

load_dotenv()
LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID"))
YEAR = int(os.getenv("ESPN_YEAR"))
ESPN_S2 = os.getenv("ESPN_S2")
SWID = os.getenv("ESPN_SWID")


def get_league() -> League:
    return League(
        league_id=LEAGUE_ID,
        year=YEAR,
        espn_s2=ESPN_S2,
        swid=SWID,
    )


@cached(ttl=300)  # 5 min
def get_standings():
    league = get_league()
    teams = league.teams
    # Return simple dicts for templating
    return sorted(
        [
            {
                "team": t.team_name,
                "wins": t.wins,
                "losses": t.losses,
                "points_for": t.points_for,
            }
            for t in teams
        ],
        key=lambda x: (-x["wins"], -x["points_for"]),
    )


@cached(ttl=180)
def get_scoreboard():
    league = get_league()
    sb = league.scoreboard()
    out = []
    for m in sb:
        out.append(
            {
                "home": m.home_team.team_name,
                "home_score": round(m.home_score, 2),
                "away": m.away_team.team_name,
                "away_score": round(m.away_score, 2),
            }
        )
    return out


@cached(ttl=600)
def get_free_agents(position: str | None = None):
    league = get_league()
    fa = league.free_agents(position=position) if position else league.free_agents()
    # Trim to a lighter payload for the template
    return [
        {
            "name": p.name,
            "pos": p.position,
            "pro_team": p.proTeam,
            "proj": getattr(p, "projected_total_points", None),
        }
        for p in fa[:200]
    ]
