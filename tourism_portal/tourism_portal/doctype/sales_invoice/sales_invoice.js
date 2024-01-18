// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		if (! frm.is_new()){
			frm.add_custom_button(__('Print Voucher'), function() {
				window.open(frappe.urllib.get_full_url("/api/method/tourism_portal.api.pdf.print_invoice_voucher?invoice_no=" + frm.doc.name));
			});
			frm.add_custom_button(__('Print Invoice'), function() {
				window.open(frappe.urllib.get_full_url("/api/method/tourism_portal.api.pdf.print_invoice_invoice?invoice_no=" + frm.doc.name));
			});
		}
	}
});
