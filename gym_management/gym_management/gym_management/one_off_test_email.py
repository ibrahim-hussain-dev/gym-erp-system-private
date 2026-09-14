import frappe

def run():
    frappe.sendmail(
        recipients=["iibrahimhere@gmail.com"],
        subject="Gym ERP — SMTP test",
        message="If you're reading this in your inbox, outgoing email from app.impacthealth.pk is working.",
        now=True,
    )
    print("Queued/sent. Check the Email Queue list in the desk if it doesn't arrive.")
