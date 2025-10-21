"""Test UniFi Controller migration"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.migrations.add_unifi_controller import apply_migration

# Apply to test database
test_db = Path(__file__).parent / "test_unifi.db"
apply_migration(test_db)

print("\n✅ Migration test completed successfully!")
