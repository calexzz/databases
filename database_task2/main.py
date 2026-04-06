import sqlite3
import csv

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

def load_csv_to_table(cursor, csv_path, table, columns):
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [tuple(row[col] for col in columns) for row in reader]
    placeholders = ", ".join("?" * len(columns))
    cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)

cursor.executescript("""        
    CREATE TABLE уровень_обучения (
        id_уровня INTEGER PRIMARY KEY,
        название VARCHAR(50));
        
    CREATE TABLE направления (
        id_направления INTEGER PRIMARY KEY,
        название VARCHAR(50));
        
    CREATE TABLE типы_обучения (
        id_типа INTEGER PRIMARY KEY,
        название VARCHAR(50));
        
    CREATE TABLE студенты (
        id_студента INTEGER PRIMARY KEY,
        id_уровня INTEGER REFERENCES уровень_обучения(id_уровня),
        id_направления INTEGER REFERENCES направления(id_направления),
        id_типа_обучения INTEGER REFERENCES типы_обучения(id_типа),
        фамилия VARCHAR(50),
        имя VARCHAR(50),
        отчество VARCHAR(50),
        средний_балл INTEGER);
""")

load_csv_to_table(cursor, "levels.csv", "уровень_обучения", ["id_уровня", "название"])
load_csv_to_table(cursor, "study_types.csv", "типы_обучения", ["id_типа", "название"])
load_csv_to_table(cursor, "routes.csv", "направления", ["id_направления", "название"])

with open('students.csv', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("""
            INSERT INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
               row['id_студента'],
               row['id_уровня'],
               row['id_направления'],
               row['id_типа_обучения'],
               row['фамилия'],
               row['имя'],
               row['отчество'],
               row['средний_балл']
            ))

print("Количество всех студентов")
cursor.execute("SELECT COUNT(*) FROM студенты")
print(cursor.fetchone()[0])

print("\nКоличество студентов по направлениям")
cursor.execute("""
    SELECT н.название, COUNT(*) as количество
    FROM студенты с
    JOIN направления н ON с.id_направления = н.id_направления
    GROUP BY н.название
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\nКоличество студентов по формам обучения")
cursor.execute("""
    SELECT т.название, COUNT(*) as количество
    FROM студенты с
    JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
    GROUP BY т.название
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\nМакс / Мин / Средний балл по направлениям")
cursor.execute("""
    SELECT н.название, 
           MAX(с.средний_балл), 
           MIN(с.средний_балл), 
           ROUND(AVG(с.средний_балл), 2)
    FROM студенты с
    JOIN направления н ON с.id_направления = н.id_направления
    GROUP BY н.название
""")
for row in cursor.fetchall():
    print(f"{row[0]}: макс={row[1]}, мин={row[2]}, средний={row[3]}")

print("\nСредний балл по направлениям, уровням и формам обучения")
cursor.execute("""
    SELECT н.название, у.название, т.название, 
           ROUND(AVG(с.средний_балл), 2)
    FROM студенты с
    JOIN направления н ON с.id_направления = н.id_направления
    JOIN уровень_обучения у ON с.id_уровня = у.id_уровня
    JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
    GROUP BY н.название, у.название, т.название
""")
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} | средний балл: {row[3]}")

print("\nТоп-5 студентов на повышенную стипендию")
cursor.execute("""
    SELECT с.фамилия, с.имя, с.отчество, с.средний_балл
    FROM студенты с
    JOIN направления н ON с.id_направления = н.id_направления
    JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
    WHERE н.название = 'Прикладная Информатика'
      AND т.название = 'Очное'
    ORDER BY с.средний_балл DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"{row[0]} {row[1]} {row[2]} — {row[3]} баллов")

print("\nОднофамильцы:")
cursor.execute("""
    SELECT фамилия, COUNT(*) as количество
    FROM студенты
    GROUP BY фамилия
    HAVING COUNT(*) > 1
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"{row[0]}: {row[1]} человека")
else:
    print("Однофамильцев нет")

print("\nПолные тёзки:")
cursor.execute("""
    SELECT фамилия, имя, отчество, COUNT(*) as количество
    FROM студенты
    GROUP BY фамилия, имя, отчество
    HAVING COUNT(*) > 1
""")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"{row[0]} {row[1]} {row[2]}: {row[3]} человека")
else:
    print("Полных тёзок нет")

conn.commit()
conn.close()

