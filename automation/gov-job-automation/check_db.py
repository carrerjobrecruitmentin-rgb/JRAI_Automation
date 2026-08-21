import pymysql
connection = pymysql.connect(host='localhost', user='root', password='', database='job_recruitment_ai', cursorclass=pymysql.cursors.DictCursor)
with connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT status, count(*) FROM jobs GROUP BY status")
        for row in cursor.fetchall():
            print(row)
        cursor.execute("SELECT count(*) FROM jobs")
        print("Total jobs:", cursor.fetchone())
