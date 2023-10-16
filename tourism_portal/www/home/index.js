$(document).ready(function () {
    $('.select2-select').each(function (i, select) {
        var icons = $(this).siblings('i');
        var labels = $(this).siblings('label');
        var placeholder = '';
        if (icons.length > 0) {
            placeholder += $(this).siblings('i').prop('outerHTML');
            $(this).siblings('i').hide();
        }
        if (labels.length > 0) {
            placeholder += $(this).siblings('label').prop('outerHTML');
            $(this).siblings('label').hide();
        }
        $(this).select2({
            theme: 'bootstrap-5',
            placeholder: placeholder,
            escapeMarkup: function (markup) {
                return markup;
            }
        });
    })
});
// Date Picker
$('.date-picker').each(function (i, select) {
    datepicker(this, {
        formatter: (input, date, instance) => {
            const value = date.toLocaleDateString("fr-CA")
            input.value = value // => '1/1/2099'
        }
    });

})

$('.room-select').change(function (e) {
    var roomCount = $(this).val();

})

function romCountChanged(e) {
    if (!e.value) e.value = 0;
    var paxContainer = e.parentNode.parentNode.querySelector('.pax-container');
    var html = '';
    for (var i = 0; i < e.value; i++) {
        document.querySelector('.pax-template-container .room-label').innerText = `Room ${i + 1}`
        html += document.querySelector('.pax-template-container').innerHTML;
    }
    paxContainer.innerHTML = html;
}
function childCountChanged(e) {
    if (!e.value) e.value = 0;
    var childrenContainer = e.parentNode.parentNode.querySelector('.children-container');
    var html = '';
    for (var i = 0; i < e.value; i++) {
        document.querySelector('.children-template-container .child-label').innerText = `Child ${i + 1}`
        html += document.querySelector('.children-template-container').innerHTML;
    }
    childrenContainer.innerHTML = html;
}
function collapseBtnPressed(e) {
    if (e.parentNode.querySelector('.panel-collapse').classList.toggle('show')){
        e.innerHTML = `<i class="fa fa-chevron-down" aria-hidden="true"></i>`
    }else{
        e.innerHTML = `<i class="fa fa-chevron-up" aria-hidden="true"></i>`
    }
    
}

function addTransferClicked(e) {
    var childrenContainer = e.closest('.voucher-search').querySelector('.transfer-search-container');
    if (childrenContainer.innerHTML.trim()){
        return;
    }
    var html = '';
    html += document.querySelector('.transfer-search-template').innerHTML;
    childrenContainer.innerHTML = html;
    e.style.display = 'none';
    
}