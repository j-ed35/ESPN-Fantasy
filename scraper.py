import nfl_data_py as nfl
from tools import (
    get_season, get_fantasy_positions, format_team_name,
    get_abbreviations, get_fantasy_positions
)
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import numpy as np

logger = logging.getLogger(__name__)
current_season = get_season()


def get_player_weekly_stats(player_name, year=current_season):
    """
    Fetch weekly stats for a player using nfl_data_py.
    Filters out BYE weeks automatically.
    Returns DataFrame with columns: Week, carries, rushing_yards, etc.
    """
    try:
        weekly_data = nfl.import_weekly_data([year], columns=None)
        
        # Filter for player and remove BYE weeks
        player_data = weekly_data[
            (weekly_data['player_display_name'] == player_name) &
            (weekly_data['week'] != 0)  # 0 = offseason
        ]
        
        if player_data.empty:
            logger.warning(f"No weekly data found for {player_name} in {year}")
            return None
        
        # Keep relevant columns and sort by week
        player_data = player_data[['week', 'carries', 'rushing_yards', 'rushing_tds',
                                    'receptions', 'targets', 'receiving_yards',
                                    'receiving_tds']].fillna(0)
        return player_data.sort_values('week')
    
    except Exception as e:
        logger.error(f"Error fetching weekly stats for {player_name}: {e}")
        return None


def get_schedule(player_name, year=current_season):
    """
    Get a player's team schedule for the year.
    Returns DataFrame with opponent for each week.
    """
    try:
        weekly_data = nfl.import_weekly_data([year])
        player_data = weekly_data[weekly_data['player_display_name'] == player_name]
        
        if player_data.empty:
            logger.warning(f"Schedule not found for {player_name}")
            return None
        
        team = player_data.iloc[0]['recent_team']
        schedules = nfl.import_schedules([year])
        schedules = schedules[schedules['game_type'] == 'REG']
        
        schedule = schedules[
            (schedules['home_team'] == team) |
            (schedules['away_team'] == team)
        ].sort_values('week')
        
        schedule['opponent'] = schedule.apply(
            lambda row: row['away_team'] if row['home_team'] == team else row['home_team'],
            axis=1
        )
        
        return schedule[['week', 'opponent']]
    
    except Exception as e:
        logger.error(f"Error fetching schedule for {player_name}: {e}")
        return None


def get_defense_stats(position, year=current_season):
    """
    Get opponent defensive stats aggregated by position allowed.
    Returns DataFrame with teams and points/yards allowed per position.
    """
    try:
        def_stats = nfl.import_seasonal_data([year], stat_type='defense')
        
        # Map position to relevant defense stat columns
        stat_mapping = {
            'RB': ['rushing_yards_allowed', 'rushing_tds_allowed', 'carries_allowed'],
            'WR': ['receiving_yards_allowed', 'receiving_tds_allowed', 'targets_allowed'],
            'TE': ['receiving_yards_allowed', 'receiving_tds_allowed', 'targets_allowed']
        }
        
        if position not in stat_mapping:
            logger.warning(f"No defense stats for position {position}")
            return None
        
        cols = ['team'] + stat_mapping[position]
        available = [col for col in cols if col in def_stats.columns]
        return def_stats[available]
    
    except Exception as e:
        logger.error(f"Error fetching defense stats for {position}: {e}")
        return None


def calculate_z_score_projection(player_name, year=current_season):
    """
    Calculate player projection using z-score method.
    
    Process:
    1. Get player's historical stats (mean, std dev)
    2. Get defense stats for remaining opponents (z-score)
    3. Project points = player_mean + z_score * player_std_dev
    
    Returns tuple: (projections_list, completed_games_list, position)
    """
    try:
        from nfl_data import get_player_stats
        
        # Get position
        player_stats = get_player_stats(player_name, year)
        if not player_stats:
            return None, None, None
        
        position = player_stats.get('position')
        
        # Get weekly stats
        weekly = get_player_weekly_stats(player_name, year)
        if weekly is None or len(weekly) < 4:
            # Try previous year for context
            prev_weekly = get_player_weekly_stats(player_name, year - 1)
            if prev_weekly is None or (len(weekly or []) + len(prev_weekly or [])) < 4:
                logger.warning(f"Insufficient data for {player_name}")
                return None, None, None
            weekly = np.concat([weekly, prev_weekly]) if weekly is not None else prev_weekly
        
        # Calculate player stats
        relevant_col = 'receiving_yards' if position in ['WR', 'TE'] else 'rushing_yards'
        player_mean = weekly[relevant_col].mean()
        player_std = weekly[relevant_col].std()
        
        if player_std == 0:
            player_std = 1  # Avoid division by zero
        
        # Get defense stats
        def_stats = get_defense_stats(position, year)
        if def_stats is None:
            return None, None, None
        
        defense_mean = def_stats[relevant_col + '_allowed'].mean()
        defense_std = def_stats[relevant_col + '_allowed'].std()
        
        if defense_std == 0:
            defense_std = 1
        
        # Get schedule
        schedule = get_schedule(player_name, year)
        if schedule is None:
            return None, None, None
        
        projections = []
        completed_games = []
        current_week = weekly['week'].max()
        
        for _, row in schedule.iterrows():
            if row['week'] <= current_week:
                # Game played
                week_data = weekly[weekly['week'] == row['week']]
                if not week_data.empty:
                    completed_games.append(float(week_data[relevant_col].iloc[0]))
            else:
                # Future game
                opponent = row['opponent']
                opp_stats = def_stats[def_stats['team'] == opponent]
                
                if not opp_stats.empty:
                    opp_allowed = float(opp_stats[relevant_col + '_allowed'].iloc[0])
                    z_score = (opp_allowed - defense_mean) / defense_std
                    projection = player_mean + z_score * player_std
                    projections.append(max(0, projection))  # No negative projections
        
        return projections, completed_games, position
    
    except Exception as e:
        logger.error(f"Error calculating projection for {player_name}: {e}")
        return None, None, None


def get_mass_projections(players=None, year=current_season, max_workers=5):
    """
    Calculate projections for multiple players using thread pool.
    
    Args:
        players: List of player names. If None, fetches top 50 per position.
        year: Season year
        max_workers: Number of concurrent threads
    
    Returns list of [player_name, position, avg_projection]
    """
    if players is None:
        from nfl_data import get_all_names
        players = get_all_names(year)[:50]
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(calculate_z_score_projection, player, year): player
            for player in players
        }
        
        for future in as_completed(futures):
            try:
                projections, _, position = future.result()
                player = futures[future]
                
                if projections and len(projections) > 0:
                    avg_projection = sum(projections) / len(projections)
                    results.append([player, position.upper(), round(avg_projection, 1)])
            except Exception as e:
                logger.error(f"Error processing player projection: {e}")
    
    return results