import os
import sys

def cleanup():
    print("Cleaning up migration issues...")
    
    # 1. Delete existing migration files
    migration_dir = "gallery/migrations"
    if os.path.exists(migration_dir):
        for file in os.listdir(migration_dir):
            if file != "__init__.py":
                file_path = os.path.join(migration_dir, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    
    # 2. Delete database
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("Deleted: db.sqlite3")
    
    print("\nCleanup complete!")
    print("\nNow run these commands:")
    print("1. python3 manage.py makemigrations gallery")
    print("2. python3 manage.py migrate")
    print("3. python3 manage.py createsuperuser")
    print("4. python3 manage.py runserver")

if __name__ == "__main__":
