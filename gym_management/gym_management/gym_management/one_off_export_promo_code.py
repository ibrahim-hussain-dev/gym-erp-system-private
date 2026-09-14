import frappe
from frappe.modules.export_file import export_to_files

def run():
    export_to_files(record_list=[["DocType", "Gym Promo Code"]], create_init=True)
    print("Exported Gym Promo Code to files.")
