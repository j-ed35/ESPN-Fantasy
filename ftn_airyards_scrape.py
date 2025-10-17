from pathlib import Path
import requests
import pandas as pd
import time
import re

BASE = "https://ha4sz2s77h.execute-api.us-east-1.amazonaws.com/test/stathub/airYards"
COMMON_PARAMS = {
    "fppg": "Half PPR",
    "positions": "RB,WR",
    "years": "2025",
}
WEEKS = range(1, 7)  # change if you only want certain weeks

OUTDIR = Path("data/ftn_airyards")
OUTDIR.mkdir(parents=True, exist_ok=True)
combined = []


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Map API keys -> tidy snake_case
    rename = {
        "playerId": "player_id",
        "name": "player",
        "team": "team",
        "position": "pos",
        "games": "g",
        "snaps": "snaps",
        "targets": "targets",
        "receptions": "rec",
        "receivingYards": "rec_yds",
        "touchdowns": "td",
        "airYards": "air_yds",
        "averageDepthOfTarget": "adot",
        "racr": "racr",
        "wopr": "wopr",
        "yardsAfterCatch": "yac",
        "targetPercentage": "target_pct",
        "airPercentage": "air_pct",
        "pprFantasyPoints": "ppr_pts",
        "halfPprFantasyPoints": "half_ppr_pts",
        "standardFantasyPoints": "std_pts",
        "pprFantasyPointsPerGame": "ppr_ppg",
        "halfPprFantasyPointsPerGame": "half_ppr_ppg",
        "standardFantasyPointsPerGame": "std_ppg",
        "touches": "touches",
        "touchesPerGame": "touches_pg",
        "team_name": "team_name",
    }
    df = df.rename(columns=rename)

    # Clean up player name (collapse multiple spaces)
    if "player" in df.columns:
        df["player"] = (
            df["player"].astype(str).map(lambda s: re.sub(r"\s{2,}", " ", s).strip())
        )

    # Order useful columns first if present
    preferred = [
        "week",
        "player_id",
        "player",
        "pos",
        "team",
        "team_name",
        "g",
        "snaps",
        "targets",
        "rec",
        "rec_yds",
        "air_yds",
        "yac",
        "td",
        "adot",
        "racr",
        "wopr",
        "target_pct",
        "air_pct",
        "half_ppr_pts",
        "ppr_pts",
        "std_pts",
        "half_ppr_ppg",
        "ppr_ppg",
        "std_ppg",
        "touches",
        "touches_pg",
    ]
    cols = [c for c in preferred if c in df.columns] + [
        c for c in df.columns if c not in preferred
    ]
    return df[cols]


session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141 Safari/537.36"
    }
)

for w in WEEKS:
    params = {**COMMON_PARAMS, "weeks": str(w)}
    try:
        r = session.get(BASE, params=params, timeout=30)
        r.raise_for_status()
        payload = r.json()
        # API returns either a dict with "body"/"data" or a raw list
        rows = []
        if isinstance(payload, dict):
            rows = payload.get("body") or payload.get("data") or []
        elif isinstance(payload, list):
            rows = payload
        if not rows:
            print(f"Week {w}: no rows")
            continue

        df = pd.DataFrame(rows)
        df.insert(0, "week", w)
        df = normalize_columns(df)

        # Save per-week CSV
        per_week_path = OUTDIR / f"ftn_airyards_2025_w{w}.csv"
        df.to_csv(per_week_path, index=False)
        print(f"Week {w}: {len(df)} rows -> {per_week_path}")

        combined.append(df)
        time.sleep(0.25)  # be polite

    except requests.HTTPError as e:
        print(f"Week {w}: HTTP {e.response.status_code}")
    except Exception as e:
        print(f"Week {w}: error {e}")

if combined:
    all_df = pd.concat(combined, ignore_index=True)
    all_out = OUTDIR / "ftn_airyards_2025_all.csv"
    all_df.to_csv(all_out, index=False)
    print(f"Combined: {len(all_df)} rows -> {all_out}")
else:
    print("No data collected.")
