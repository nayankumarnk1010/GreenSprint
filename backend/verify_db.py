from sqlalchemy import inspect

from app.db.session import engine

inspector = inspect(engine)

print("Tables Found:")
print(inspector.get_table_names())

print("\nUsers Table Columns:")

for column in inspector.get_columns("users"):
    print(
        f"{column['name']} - {column['type']}"
    )