var formViewModel = {};
var requestViewModel = {};

Date.prototype.formatYYYYMMDD = function(){
    return (this.getFullYear()) + 
    "-" +  this.getMonth() + 1 +
    "-" +  this.getDate();
}

ko.bindingHandlers.datepicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {

        var unwrap = ko.utils.unwrapObservable;
        var dataSource = valueAccessor();
        var binding = allBindingsAccessor();

        //initialize datepicker with some optional options
        var options = allBindingsAccessor().datepickerOptions || {};
        $(element).datepicker(options);
        $(element).datepicker('update', dataSource());
        //when a user changes the date, update the view model
        ko.utils.registerEventHandler(element, "changeDate", function (event) {
            var value = valueAccessor();
            if (ko.isObservable(value)) {
                value(event.date.formatYYYYMMDD());
            }
        });
    },
    update: function (element, valueAccessor) {
        var widget = $(element).data("datepicker");

        var value = ko.utils.unwrapObservable(valueAccessor());

        //when the view model is updated, update the widget
        if (widget) {
            widget.date = value;
            if (widget.date) {
                widget.setValue();
                $(element).datepicker('update', value)
            }
        }
    }
};

var editRequest = function(request) {
    formViewModel.title(request['title']);
    formViewModel.description(request['description']);
    formViewModel.client(request['client']);
    formViewModel.priority(request['priority']);
    formViewModel.target_date(request['target_date']);
    formViewModel.product_area(request['product_area']);
    $('#createRequestModal').modal('show');
};

var submitRequest = function(formElement) {
    $.post('/req', ko.toJS(formViewModel), function(res) {
        if(res['success']) {
            $.getJSON('/req', function(data) {
                requestViewModel.requests(data);
            });
            $('#createRequestModal').modal('hide');
        } else {
            Object.keys(res).forEach(function(key, idx) {
                document.getElementById(key).setCustomValidity(res[key]);
            });
        }
    });
};

$(document).ready(function(){
    $('#requestForm').serializeArray().forEach(function(item) {
        formViewModel[item['name']] = ko.observable(item['value']);
    });
    ko.applyBindings(formViewModel, document.getElementById('requestForm'));
    
    $.getJSON('/req', function(data) {
        requestViewModel['requests'] = ko.observableArray(data);
        requestViewModel['submitRequest'] = submitRequest;
        requestViewModel['editRequest'] = editRequest;
        ko.applyBindings(requestViewModel, document.getElementById('requests'));
    });
    /*$('#createRequestModal').on('hidden.bs.modal', function () {
        $(this).find('input,textarea').not('input[type="submit"]').val('').end();
        $(this).find('select').selectedIndex = 0;
    });*/
});

