# Fantasy Playbook V2

A FastAPI web application for managing and viewing ESPN Fantasy Football league information.

## Features

- **League Overview**: View your league's basic information
- **Standings**: Check current team standings with wins, losses, and points
- **Matchups**: See current week's matchups and scores
- **Waivers**: Browse available free agents by position

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: HTML templates with Jinja2
- **Data Source**: ESPN Fantasy Football API
- **Cache**: Custom TTL-based caching system

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd Fantasy-Playbook-V2
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your ESPN league credentials:
   ```
   ESPN_LEAGUE_ID=your_league_id
   ESPN_YEAR=2025
   ESPN_S2=your_espn_s2_cookie
   ESPN_SWID=your_swid_cookie
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

6. Open your browser to `http://127.0.0.1:8000`

## Getting ESPN Credentials

To get your ESPN_S2 and SWID cookies:
1. Log into ESPN Fantasy Football in your browser
2. Open browser developer tools (F12)
3. Go to Application/Storage > Cookies
4. Find `espn.com` and copy the values for `espn_s2` and `SWID`

## Project Structure

```
├── main.py              # FastAPI application and routes
├── espn_client.py       # ESPN API integration
├── services/
│   └── cache.py         # Caching utilities
├── static/
│   └── main.css         # Styling
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── standings.html
│   ├── matchups.html
│   └── waivers.html
└── requirements.txt     # Python dependencies
```

## API Endpoints

- `GET /` - Home page
- `GET /standings` - League standings
- `GET /matchups` - Current matchups
- `GET /waivers` - Free agents (optional position filter: `?pos=QB`)