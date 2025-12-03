from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Add color column
            connection.execute(text("ALTER TABLE carrito_item ADD COLUMN color VARCHAR(50);"))
            print("Added color column")
        except Exception as e:
            print(f"Error adding color column (might already exist): {e}")

        try:
            # Add talla column
            connection.execute(text("ALTER TABLE carrito_item ADD COLUMN talla VARCHAR(20);"))
            print("Added talla column")
        except Exception as e:
            print(f"Error adding talla column (might already exist): {e}")
            
        connection.commit()

if __name__ == "__main__":
    migrate_db()
