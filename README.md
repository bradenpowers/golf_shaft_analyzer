# ⛳ Golf Shaft Analytics

A searchable, filterable database and analysis platform for golf shaft specifications. Compare shafts across manufacturers by flex, weight, torque, launch profile, and spin characteristics to make data-driven equipment decisions.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

## Why This Exists

Club fitting is increasingly data-driven, but shaft specification data is scattered across manufacturer websites, PDF catalogs, and fitting cart spreadsheets. There's no single place to search, compare, and analyze shaft specs across brands in a structured format.

This project solves that by:

- **Normalizing** shaft specs from multiple manufacturers into a consistent schema
- **Providing** a fast, filterable web interface for searching and comparing shafts
- **Enabling** data analysis on shaft characteristics (weight progression, torque profiles, flex patterns)
- **Exposing** a REST API for integration with other golf analytics tools

## Features

- **Multi-manufacturer database** — Specs from major shaft OEMs (Project X, Fujikura, Mitsubishi, Graphite Design, Aldila, UST Mamiya, and more)
- **Advanced filtering** — Filter by club type, flex, weight range, torque range, launch profile, spin profile, and price range
- **Side-by-side comparison** — Select up to 4 shafts and compare all specs in a unified view
- **Weight/torque visualization** — Interactive charts showing how shaft characteristics vary across a product line
- **Flex comparison** — Normalized flex ratings to compare across manufacturers (one brand's Stiff is another's X-Stiff)
- **CSV/JSON export** — Download filtered results for your own analysis
- **REST API** — Programmatic access to the full database

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/golf-shaft-analytics.git
cd golf-shaft-analytics
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Load Sample Data

```bash
python -m src.ingestion.load_data
```

### Run the App

```bash
streamlit run app/Home.py
```

The app will open at `http://localhost:8501`.

### Run the API

```bash
uvicorn src.api.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Project Structure

```
golf-shaft-analytics/
├── app/                    # Streamlit web application
│   ├── Home.py             # Main page — search & filter
│   └── pages/
│       ├── 1_Compare.py    # Side-by-side shaft comparison
│       └── 2_Analysis.py   # Data visualizations & analysis
├── data/
│   ├── raw/                # Original manufacturer data (CSV, PDF extracts)
│   └── processed/          # Normalized, cleaned shaft database
├── src/
│   ├── ingestion/          # Data loading and normalization
│   │   ├── load_data.py    # Main data loader
│   │   ├── normalizer.py   # Schema normalization logic
│   │   └── schemas.py      # Data models and validation
│   ├── analysis/           # Analysis and comparison logic
│   │   └── compare.py      # Shaft comparison utilities
│   └── api/                # FastAPI REST API
│       └── main.py         # API endpoints
├── tests/                  # Unit tests
│   ├── test_normalizer.py
│   └── test_schemas.py
├── docs/                   # Additional documentation
│   └── DATA_SOURCES.md     # Where shaft data comes from
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Schema

Every shaft in the database is normalized to this schema:

| Field | Type | Description |
|-------|------|-------------|
| `manufacturer` | string | Shaft OEM (e.g., "Project X", "Fujikura") |
| `model` | string | Product line (e.g., "HZRDUS Black", "Ventus Blue") |
| `generation` | string | Generation/version if applicable |
| `club_type` | enum | `woods`, `fairway`, `hybrid`, `iron`, `wedge`, `putter` |
| `flex` | enum | `Ladies`, `Senior`, `Regular`, `Stiff`, `X-Stiff`, `TX` |
| `weight_grams` | float | Shaft weight in grams |
| `length_inches` | float | Raw/uncut length in inches |
| `torque_degrees` | float | Torque in degrees |
| `launch` | enum | `Low`, `Low-Mid`, `Mid`, `Mid-High`, `High` |
| `spin` | enum | `Low`, `Low-Mid`, `Mid`, `Mid-High`, `High` |
| `butt_diameter_inches` | float | Butt diameter |
| `tip_diameter_inches` | float | Tip diameter (0.335 or 0.355 for woods, 0.370 for irons) |
| `tip_stiff` | enum | `Soft`, `Medium`, `Firm`, `Very Firm` |
| `kickpoint` | enum | `Low`, `Low-Mid`, `Mid`, `Mid-High`, `High` |
| `material` | string | Construction (e.g., "graphite", "steel", "multi-material") |
| `msrp_usd` | float | Retail price in USD |

## Contributing

Contributions are welcome, especially:

- **New shaft data** — If you have spec sheets or catalog data for shafts not yet in the database
- **Data corrections** — Spotted an error? Open an issue or PR
- **New analysis features** — Ideas for useful comparisons or visualizations
- **API integrations** — Connecting this data to other golf tools

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- [ ] Expand database to 500+ shaft models
- [ ] Add frequency/CPM data where available
- [ ] Integrate with launch monitor data for shaft-to-ballflight correlation
- [ ] Shaft fitting recommendation engine based on player data
- [ ] Snowflake backend option for production-scale deployments
- [ ] Mobile-friendly UI

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

Shaft specification data is compiled from publicly available manufacturer catalogs, spec sheets, and fitting resources. This project is not affiliated with or endorsed by any shaft manufacturer.
