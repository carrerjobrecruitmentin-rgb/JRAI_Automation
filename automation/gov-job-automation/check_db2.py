import pymysql
connection = pymysql.connect(host='localhost', user='root', password='', database='jrai', cursorclass=pymysql.cursors.DictCursor)
with connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM jobs")
        print("Total jobs in jrai:", cursor.fetchone())
