
from app.database import get_connection

conn = get_connection()

try:
    rows = conn.execute(
        "SELECT id, email, role FROM users"
    ).fetchall()

    print("Users in database:")
    for row in rows:
        print(dict(row))

    email = input("Enter the exact email shown above: ").strip().lower()

    cursor = conn.execute(
        "UPDATE users SET role = ? WHERE email = ?",
        ("admin", email)
    )
    conn.commit()

    if cursor.rowcount == 1:
        print("Success! User role is now admin.")
    else:
        print("No user updated. Check the email.")

finally:
    conn.close()
