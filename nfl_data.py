import nfl_data_py as nfl
from tools import (
    get_season, get_relevant_columns, format_df, get_fantasy_positions,
    fix_repeating_name_patterns, format_team_name
)
import logging

logger = logging.getLogger(__name__)
current_season = get_season()


def get_teams_schedule(year=current_season):
    """
    Get NFL schedule for the year.
    Returns dict: {team: [opponent_week1, opponent_week2, ...]}
    """
    try:
        schedules = nfl.import_schedules([year])
        schedules = schedules[schedules['game_type'] == 'REG']
        team_schedules = {}
        
        for _, row in schedules.iterrows():
            for team, opponent in [(row['home_team'], row['away_team']),
                                    (row['away_team'], row['home_team'])]:
                if team not in team_schedules:
                    team_schedules[team] = ['BYE'] * 18
                team_schedules[team][row['week'] - 1] = opponent
        
        return team_schedules
    except Exception as e:
        logger.error(f"Error fetching schedule for {year}: {e}")
        return {}


def get_all_data(year=current_season):
    """
    Get seasonal player stats (non-PPR).
    Filters for fantasy-relevant positions and cleans data.
    """
    try:
        data = nfl.import_seasonal_data([year], "REG")
        data = format_df(data, get_relevant_columns())
        data = fix_repeating_name_patterns(data, ["player_display_name", "position"])
        data = data[data['position'].isin(get_fantasy_positions())]
        return data
    except Exception as e:
        logger.error(f"Error fetching seasonal data for {year}: {e}")
        return None


def get_all_names(year=current_season):
    """
    Get all player names sorted by total yards (proxy for production).
    Falls back to receptions if yards unavailable.
    """
    data = get_all_data(year)
    if data is None:
        return []
    
    # Sort by receiving yards as primary metric (fantasy-relevant)
    data = data.sort_values(by='receiving_yards', ascending=False)
    return data['player_display_name'].unique().tolist()


def get_player_stats(name, year=current_season):
    """
    Get seasonal stats for a specific player.
    Returns dict with all non-PPR stats.
    """
    data = get_all_data(year)
    if data is None:
        return {}
    
    row = data[data["player_display_name"] == name]
    if not row.empty:
        row_dict = row.iloc[0].to_dict()
        row_dict.pop("player_display_name", None)
        return row_dict
    else:
        logger.warning(f"Player {name} not found in {year} data")
        return {}


def get_library_ids():
    """
    Get player ID mappings from nfl_data_py.
    Useful for cross-referencing with other data sources.
    """
    try:
        ids_df = nfl.import_ids()
        columns = ['nfl_id', 'gsis_id', 'fantasy_data_id', 'position']
        available = [col for col in columns if col in ids_df.columns]
        return ids_df[available]
    except Exception as e:
        logger.error(f"Error fetching player IDs: {e}")
        return None