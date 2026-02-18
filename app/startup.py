import subprocess
import sys
from pathlib import Path

# Run data loader before app starts if processed data doesn't exist
db_file = Path(__file__).parent.parent / "data" / "processed" / "shaft_database.json"
if not db_file.exists():
    subprocess.run([sys.executable, "-m", "src.ingestion.load_data"], cwd=str(Path(__file__).parent.parent))
