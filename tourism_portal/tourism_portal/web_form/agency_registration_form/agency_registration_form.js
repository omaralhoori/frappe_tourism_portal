frappe.ready(function() {
	$('div[data-fieldtype="HTML"]').html(`
    <div class="form-group">
    <label class="control-label col-sm-4"><a target="_blank" href="{{terms_and_conditions}}">Terms and Conditions</a></label></div>`);
})