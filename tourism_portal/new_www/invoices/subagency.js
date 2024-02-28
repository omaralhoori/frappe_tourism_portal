function searchBtnClicked(e){
    var voucherNo = $('#voucher_no').val();
    if (voucherNo == '') {
        alert('Please enter voucher number');
        return;
    }
    var url = '/invoices/subagency?voucher_no=' + voucherNo;
    window.location.href = url;
}