import psycopg2

passwords = ['postgres', '', 'root', 'admin', 'password']
for p in passwords:
    try:
        print(f"Trying password '{p}'...")
        conn = psycopg2.connect(
            host='localhost',
            database='kickstarter',
            user='postgres',
            password= 'OVERLORD',
            port='5432'
        )
        print("Success with password:", p)
        conn.close()
        break
    except Exception as e:
        print(f"Failed: {repr(e)}")
