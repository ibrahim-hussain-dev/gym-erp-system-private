import frappe

def run():
    frappe.sendmail(
        recipients=["pc16705.ibrahim@gmail.com"],
        subject="Gym ERP - Test Email",
        message="<p>Ye test email hai. Agar ye mil raha hai to SMTP sahi kaam kar raha hai.</p>",
        now=True,
    )
    print("Test email sent (check inbox / spam folder).")
