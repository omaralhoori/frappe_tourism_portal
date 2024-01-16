frappe.listview_settings["Sales Invoice"] = {
	hide_name_column: true,
	add_fields: ["status"],
	get_indicator: function(doc) {
        if (doc.status=="Draft") {
			return [__("Draft"), "orange", "status,=,Draft"];
        }
        if (doc.status=="Submitted") {
			return [__("Completed"), "green", "status,=,Submitted"];
        }
        if (doc.status=="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
        }
    },
    button: {
        show: function(doc) {
            return true;
            },
        get_label: function() {
            return __('Voucher');
            },
        get_description: function(doc) {
            return ('Print {0}', [doc.name]);
            },
        action: function(doc) {
            var objWindowOpenResult = window.open(frappe.urllib.get_full_url("/api/method/tourism_portal.api.pdf.print_invoice_voucher?"
                + "invoice_no=" + encodeURIComponent(doc.name)
            ));
        if(!objWindowOpenResult) {
            msgprint("Please set permission for pop-up windows in your browser!"); 
            return;
        }
    }}
}