import pandas as pd
from pathlib import Path


class StatsLoader:
    def __init__(self, csv_dir="data"):
        self.csv_dir = Path(csv_dir)

    def load_air_yards(self):
        """Load ftn_Airyards by week"""
        df = pd.read_csv(self.csv_dir / "ftn_Airyards.csv")
        return df

    def load_snap_counts(self):
        """Load snap count percentages"""
        df = pd.read_csv(self.csv_dir / "snap_count_percentages.csv")
        return df

    def get_team_stats(self, team_name, weeks=None):
        """Get stats for specific team, optionally filter by weeks"""
        air_yards = self.load_air_yards()
        snaps = self.load_snap_counts()

        team_air = (
            air_yards[air_yards["Team"] == team_name]
            if "Team" in air_yards.columns
            else None
        )
        team_snaps = (
            snaps[snaps["Team"] == team_name] if "Team" in snaps.columns else None
        )

        if weeks:
            week_cols = [col for col in team_air.columns if col.startswith("Week")]
            week_cols = week_cols[-weeks:]
            team_air = team_air[["Team"] + week_cols]
            team_snaps = team_snaps[["Team"] + week_cols]

        return {
            "air_yards": team_air.to_dict("records") if team_air is not None else [],
            "snap_counts": team_snaps.to_dict("records")
            if team_snaps is not None
            else [],
        }
