# Contributing to Golf Shaft Analytics

Thanks for your interest in contributing! This project aims to build the most comprehensive, accurate, and useful golf shaft specification database available.

## How to Contribute

### Adding Shaft Data

The most impactful contribution is adding new shaft specifications. Here's how:

1. **Find spec data** from manufacturer websites, catalogs, or fitting resources
2. **Create a CSV** following the format in `data/raw/shaft_specs.csv`
3. **Run the normalizer** to verify your data parses correctly: `python -m src.ingestion.load_data`
4. **Submit a PR** with both the raw CSV and a note about where the data came from

### Data Corrections

If you spot an error in the database:

1. Open an issue describing the error and the correct value
2. Include a source (manufacturer spec sheet, catalog, etc.)
3. Or submit a PR with the fix

### Code Contributions

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Submit a PR

### Feature Requests

Open an issue tagged `enhancement` with a description of what you'd like to see.

## Code Style

- Python 3.11+ with type hints
- Format with `black`
- Lint with `ruff`
- Tests with `pytest`

## Data Standards

- All weights in grams
- All lengths in inches
- All torque values in degrees
- Flex values must map to: Ladies, Senior, Regular, Stiff, X-Stiff, TX
- Launch/Spin profiles must map to: Low, Low-Mid, Mid, Mid-High, High
