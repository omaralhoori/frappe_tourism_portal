function searchBtnClicked(e){
    var voucherNo = $('#voucher_no').val();
    if (voucherNo == '') {
        alert('Please enter voucher number');
        return;
    }
    var url = '/invoices?voucher_no=' + voucherNo;
    window.location.href = url;
}