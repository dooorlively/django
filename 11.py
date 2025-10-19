import os
import sqlite3


def find_databases():
    print("🔍 Поиск баз данных SQLite в проекте...")

    # Ищем все .sqlite3 файлы
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.sqlite3'):
                db_path = os.path.join(root, file)
                print(f"\n📁 Найдена база: {db_path}")

                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Получаем список таблиц
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()

                    print(f"📊 Таблицы в базе:")
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        print(f"  - {table[0]}: {count} записей")

                    conn.close()

                except Exception as e:
                    print(f"  ❌ Ошибка чтения: {e}")


if __name__ == "__main__":
    find_databases()