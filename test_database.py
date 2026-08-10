import psycopg
connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="Database: b2b_referentiel",
    user="postgres",
    password="145825"
)

print("Connected successfully")

with connection.cursor() as cursor:
    cursor.execute("SELECT id_client, nom_client FROM client LIMIT 5;")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

connection.close()