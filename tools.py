from datetime import date, datetime, timedelta, timezone
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# NFL Constants
FANTASY_POSITIONS = ["RB", "WR", "TE"]
NFL_SEASON_WEEKS = 18
CURRENT_TIMEZONE = timezone(timedelta(hours=-5))  # EST

TEAM_ABBREVIATIONS = {
    "ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills",
    "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals", "CLE": "Browns",
    "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers",
    "HOU": "Texans", "IND": "Colts", "JAC": "Jaguars", "KC": "Chiefs",
    "LA": "Rams", "LAC": "Chargers", "LAR": "Rams", "LV": "Raiders",
    "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints",
    "NYG": "Giants", "NYJ": "Jets", "OAK": "Raiders", "PHI": "Eagles",
    "PIT": "Steelers", "SD": "Chargers", "SEA": "Seahawks", "SF": "49ers",
    "STL": "Rams", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Commanders"
}

# Columns from nfl_data_py to keep (non-PPR stats)
RELEVANT_COLUMNS = [
    "player_display_name", "position", "carries", "rushing_yards", "rushing_tds",
    "receptions", "targets", "receiving_yards", "receiving_tds", "tgt_sh",
    "ry_sh", "wopr_y", "rtd_sh", "yptmpa", "games"
]


def get_season():
    """Determine current NFL season based on date."""
    current_year = datetime.now().year
    september_first = date(current_year, 9, 1)
    days_to_add = (7 - september_first.weekday()) % 7
    labor_day = september_first + timedelta(days=days_to_add)
    end_of_week_1 = labor_day + timedelta(days=7)
    today_est = datetime.now(CURRENT_TIMEZONE).date()
    return current_year if today_est > end_of_week_1 else current_year - 1


def get_abbreviations():
    """Return NFL team abbreviation to full name mapping."""
    return TEAM_ABBREVIATIONS


def get_relevant_columns():
    """Return list of NFL stat columns to track (non-PPR)."""
    return RELEVANT_COLUMNS


def get_fantasy_positions():
    """Return list of fantasy-relevant positions."""
    return FANTASY_POSITIONS


def format_team_name(team_abbr):
    """
    Convert team abbreviation to full name.
    Falls back to abbreviation if not found.
    """
    return TEAM_ABBREVIATIONS.get(team_abbr, team_abbr)


def format_df(data, columns_to_keep):
    """Keep only specified columns from DataFrame."""
    missing = [col for col in columns_to_keep if col not in data.columns]
    if missing:
        logger.warning(f"Columns not found in DataFrame: {missing}")
    available = [col for col in columns_to_keep if col in data.columns]
    return data[available]


def format_player_name(player_name):
    """
    Remove team abbreviation from player name.
    Handles formats like 'John Smith KC' or 'John Smith (KC)'.
    """
    for abbr in TEAM_ABBREVIATIONS.keys():
        if player_name.endswith(abbr):
            return player_name[:-len(abbr)].strip()
        elif player_name.endswith(f"({abbr})"):
            return player_name[:-len(abbr)-2].strip()
    return player_name


def fix_repeating_name_patterns(data, columns):
    """
    Fix player names with repeating patterns (e.g., 'JohnJohnJohn').
    Returns corrected DataFrame.
    """
    def find_repeating_pattern(text):
        full_len = len(text)
        for i in range(1, full_len):
            pattern = text[:i]
            reps = full_len / len(pattern)
            if full_len % len(pattern) == 0 and text == pattern * int(reps):
                return pattern
        return text

    data_copy = data.copy()
    for col in columns:
        if col in data_copy.columns:
            data_copy[col] = data_copy[col].apply(find_repeating_pattern)
    return data_copy