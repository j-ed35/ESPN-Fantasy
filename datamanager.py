from scraper import get_player_weekly_stats
from tools import get_season, NFL_SEASON_WEEKS
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages cached player weekly stats and provides formatted access.
    Lazily loads data on first request.
    """
    
    def __init__(self):
        self.df = {}  # {player_name: DataFrame}
        self.stat_columns = [
            'week', 'carries', 'rushing_yards', 'rushing_tds',
            'receptions', 'targets', 'receiving_yards', 'receiving_tds'
        ]
    
    def get_df(self):
        """Return all cached DataFrames."""
        return self.df
    
    def add_new_player_data(self, player_name, year=None):
        """
        Fetch and cache weekly stats for a player.
        Logs warning if data fetch fails.
        """
        try:
            if year is None:
                year = get_season()
            
            weekly_data = get_player_weekly_stats(player_name, year)
            
            if weekly_data is None:
                logger.warning(f"Failed to fetch data for {player_name}")
                self.df[player_name] = pd.DataFrame(columns=['week'])
            else:
                self.df[player_name] = weekly_data
        
        except Exception as e:
            logger.error(f"Exception loading data for {player_name}: {e}")
            self.df[player_name] = pd.DataFrame(columns=['week'])
    
    def get_stat_by_week(self, player_name, stat_name):
        """
        Get player's stat for each week as a list (18 weeks).
        Missing weeks are NaN.
        
        Args:
            player_name: Player name
            stat_name: Stat column (e.g., 'rushing_yards', 'receiving_tds')
        
        Returns list of 18 values (weeks 1-18)
        """
        if player_name not in self.df:
            self.add_new_player_data(player_name)
        
        player_df = self.df[player_name]
        stat_list = []
        
        for week in range(1, NFL_SEASON_WEEKS + 1):
            week_data = player_df[player_df['week'] == week]
            
            if not week_data.empty and stat_name in week_data.columns:
                try:
                    value = float(week_data[stat_name].iloc[0])
                    stat_list.append(value)
                except (ValueError, TypeError):
                    stat_list.append(float('nan'))
            else:
                stat_list.append(float('nan'))
        
        return stat_list
    
    def get_data(self, players, stat_name):
        """
        Get stat data for multiple players.
        
        Args:
            players: List of player names
            stat_name: Stat to retrieve (e.g., 'rushing_yards')
        
        Returns list of [player_name, [week1_stat, week2_stat, ...]]
        """
        output = []
        
        for player in players:
            try:
                stat_data = self.get_stat_by_week(player, stat_name)
                output.append([player, stat_data])
            except Exception as e:
                logger.error(f"Error getting stat {stat_name} for {player}: {e}")
        
        return output
    
    def clear(self):
        """Clear all cached data."""
        self.df = {}
        logger.info("DataManager cache cleared")