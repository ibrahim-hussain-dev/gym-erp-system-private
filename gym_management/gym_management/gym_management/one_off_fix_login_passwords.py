import frappe
from frappe.utils.password import update_password, check_password
import secrets, string

def gen_password(n=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(n))

def run():
    for email in ["owner@gym.local", "fd1@gym.local"]:
        if not frappe.db.exists("User", email):
            print(email, "-> USER DOES NOT EXIST")
            continue
        new_pw = gen_password()
        update_password(user=email, pwd=new_pw, logout_all_sessions=1)
        frappe.db.commit()
        try:
            check_password(email, new_pw)
            status = "VERIFIED OK"
        except Exception as e:
            status = f"STILL FAILING: {e}"
        print(email, "-> new password:", new_pw, "|", status)

    print("DONE")
