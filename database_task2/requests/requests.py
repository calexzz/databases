import sqlite3
import csv

conn = sqlite3.connect('../students.db')
cursor = conn.cursor()

print("Категория успеваемости: ")
cursor.execute("""
    SELECT фамилия, имя, средний_балл,
    CASE
        WHEN средний_балл >= 90 THEN 'Отличник'
        WHEN средний_балл >= 75 THEN 'Хорошист'
        WHEN средний_балл >= 60 THEN 'Удовлетворительно'
        ELSE 'Неуспевающий'
    END AS категория
FROM студенты;
""")
for row in cursor.fetchall():
    print(f"{row[1]} {row[0]}: средний балл={row[2]} {row[3]}")

print('\nПодсчёт студентов по уровням обучения')
cursor.execute("""
    SELECT
    SUM(CASE WHEN у.название = 'Бакалавриат' THEN 1 ELSE 0 END) AS бакалавры,
    SUM(CASE WHEN у.название = 'Магистратура' THEN 1 ELSE 0 END) AS магистры,
    SUM(CASE WHEN у.название = 'Аспирантура'  THEN 1 ELSE 0 END) AS аспиранты

    FROM студенты с
    JOIN уровень_обучения у ON с.id_уровня = у.id_уровня;
""")
б, м, а = cursor.fetchone()
print(f"Бакалавры: {б}, Магистры: {м}, Аспиранты: {а}")

cursor.execute("""
    SELECT с.фамилия, с.имя, с.средний_балл, н.название
    FROM студенты с
    JOIN направления н ON с.id_направления = н.id_направления
    WHERE с.средний_балл > (
        SELECT AVG(средний_балл)
        FROM студенты
        WHERE id_направления = с.id_направления
    )
""")
print("\nСтуденты с баллом выше среднего по своему направлению")
for фамилия, имя, балл, направление in cursor.fetchall():
    print(f"{фамилия} {имя} — {балл} баллов ({направление})")

cursor.execute("""
    SELECT название
    FROM направления
    WHERE id_направления IN (
        SELECT DISTINCT id_направления
        FROM студенты
        WHERE средний_балл >= 90
    )
""")
print("\nНаправления, где есть хотя бы один отличник (балл >= 90)")
for row in cursor.fetchall():
    print(f"{row[0]}")

cursor.execute("""
    WITH ranked AS (
        SELECT с.фамилия, с.имя, с.средний_балл, н.название AS направление,
               RANK() OVER (PARTITION BY с.id_направления ORDER BY с.средний_балл DESC) AS место
        FROM студенты с
        JOIN направления н ON с.id_направления = н.id_направления
    )
    SELECT * FROM ranked WHERE место = 1;
""")
print("\nЛучший студент каждого направления")
for фамилия, имя, балл, направление, место in cursor.fetchall():
    print(f"{направление}: {фамилия} {имя} — {балл} баллов")

cursor.execute("""
    WITH avg_by_direction AS (
        SELECT н.название AS направление,
               ROUND(AVG(с.средний_балл), 2) AS средний_балл
        FROM студенты с
        JOIN направления н ON с.id_направления = н.id_направления
        GROUP BY н.название
    )
    SELECT * FROM avg_by_direction
    WHERE средний_балл > (SELECT AVG(средний_балл) FROM студенты);
""")
print("\nНаправления с баллом выше общего среднего")
for направление, балл in cursor.fetchall():
    print(f"{направление}: {балл}")

conn.commit()
conn.close()
