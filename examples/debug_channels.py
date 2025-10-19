import sys

sys.path.insert(0, "src")

from alerts import AlertManager, NotificationChannel
from database.database import Database

db = Database(":memory:")
db.initialize()
db.initialize_alerts()

manager = AlertManager(db)

# Create channel
c = NotificationChannel(
    id="test-1", name="Test", channel_type="email", config={}, enabled=True
)
created = manager.create_channel(c)
print(f"Created: {created.id}")

# List channels
channels = manager.list_channels()
print(f"Total channels: {len(channels)}")
for ch in channels:
    print(f"  - {ch.id}: {ch.name}")

manager.close()
