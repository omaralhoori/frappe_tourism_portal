import frappe


def send_invoice_notification(doc, method):
    if doc.docstatus == 1:
        company= doc.company
        email = frappe.db.get_value("Company", company, "contact_email", cache=True)
        if not email:
            return
        frappe.sendmail(
            recipients=[email],
            sender=None,
            subject="Invoice {} is ready".format(doc.name),
            message="Dear {},\n\nYour invoice {} is ready.\n\nBest regards,\n\n{}".format(
                doc.customer_name, doc.name, frappe.session.user
            ),
        )
        print("email sent")
