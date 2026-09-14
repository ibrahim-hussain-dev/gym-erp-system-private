import frappe
import secrets, string

def gen_password(n=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(n))

def make_user(email, full_name, role, password):
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = full_name
    user.enabled = 1
    user.user_type = "System User"
    user.send_welcome_email = 0
    user.new_password = password
    user.roles = []
    user.append("roles", {"role": role})
    if user.is_new():
        user.insert(ignore_permissions=True)
    else:
        user.save(ignore_permissions=True)
    return user

def run():
    owner_pw = gen_password()
    fd_pw = gen_password()

    make_user("owner@gym.local", "Gym Owner", "Gym Owner", owner_pw)
    make_user("fd1@gym.local", "Front Desk", "Gym Front Desk", fd_pw)

    frappe.db.commit()
    print("=========================================")
    print("Owner login:      owner@gym.local")
    print("Owner password:   " + owner_pw)
    print("-----------------------------------------")
    print("Front Desk login: fd1@gym.local")
    print("Front Desk pw:    " + fd_pw)
    print("=========================================")
    print("DONE")
