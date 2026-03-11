import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='kickstarter',
        user='postgres',
        password='OVERLORD',
        port='5432'
    )
    print("Success")
except Exception as e:
    import sys
    import traceback
    sys.excepthook(*sys.exc_info())
    print("\nRaw args:", e.args)
    if e.args and isinstance(e.args[0], bytes):
        print("Decoded:", e.args[0].decode('cp1252', 'ignore'))
