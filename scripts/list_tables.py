"""List database tables."""
import sqlite3

conn = sqlite3.connect('network_monitor.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print('Tables in database:')
for t in tables:
    print(f'  - {t[0]}')
conn.close()
