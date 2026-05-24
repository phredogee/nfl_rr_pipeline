# NFL RR Pipeline

A data pipeline that ingests NFL schedules, rosters, and weekly stats into a PostgreSQL database for analysis.

## Stack

- **Python 3.13** — ingestion scripts
- **PostgreSQL 16** — database (via Docker)
- **nfl_data_py** — NFL data source
- **psycopg2** — Python/Postgres connector
- **pandas** — data shaping and cleaning
- **Docker Compose** — database orchestration

## Project Structure
nfl_rr_pipeline/
├── config/
│   ├── db_config.py        # database connection settings (not committed)
│   └── schema.sql          # table definitions
├── queries/
│   └── sanity_sweep.sql    # 5 data validation queries
├── src/
│   └── ingest.py           # pulls NFL data and loads into Postgres
├── docker-compose.yml      # spins up Postgres container
└── requirements.txt        # Python dependencies

## Setup

### 1. Prerequisites
- Docker Desktop running
- Python 3.13 with WSL2/Debian
- Git

### 2. Clone the repo
```bash
git clone https://github.com/phredogee/nfl_rr_pipeline.git
cd nfl_rr_pipeline
```

### 3. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install numpy pandas psycopg2-binary pyarrow appdirs
pip install nfl-data-py --no-deps
```

### 4. Create db_config.py
Create `config/db_config.py` (not committed for security):
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "nfl_rr_pipeline",
    "user": "your_user",
    "password": "your_password"
}
```

### 5. Start the database
```bash
docker compose up -d
```

### 6. Run ingestion
```bash
python3 src/ingest.py
```

### 7. Validate data
```bash
docker exec -i nfl_pipeline_db psql -U your_user -d nfl_rr_pipeline -f /dev/stdin < queries/sanity_sweep.sql
```

## Data

| Table | Description | Rows (2023–2024) |
|---|---|---|
| `schedules` | One row per game | 570 |
| `rosters` | One row per player per season | 6,304 |
| `weekly_stats` | One row per player per week | 11,250 |

## Sanity Sweep Results

All 5 validation queries passing clean on 2023–2024 data:

- ✅ Row counts verified across all tables
- ✅ Both seasons present and balanced
- ✅ Zero nulls on critical columns
- ✅ Weeks 1–18 for both seasons, no garbage data
- ✅ Top fantasy scorers show realistic values

## Roadmap

- [ ] Live API integration when 2025 preseason opens
- [ ] Automated ingestion scheduling
- [ ] Jupyter notebook for analysis and visualization
- [ ] Dashboard for weekly stats tracking