
function checkNecessaryFields(){
    if(document.querySelector("#from_date").value && document.querySelector("#to_date").value)
    return true
    
    return false
}

$(document).ready(function () {
    formatDataPicker(() =>{
        if(checkNecessaryFields())
        {
            location.href = location.origin + '/account/statement' + '?from_date=' + document.querySelector("#from_date").value + '&to_date=' +  document.querySelector("#to_date").value
        }
    });
});

function formatDataPicker(onchange) {
    $('.date-picker').each(function (i, select) {
        datepicker(this, {
            formatter: (input, date, instance) => {
                const value = date.toLocaleDateString("fr-CA")
                input.value = value // => '1/1/2099'
            },
            onSelect:  onchange,
        });

    })

}