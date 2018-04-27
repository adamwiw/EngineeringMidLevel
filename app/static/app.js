$(document).ready(function(){
    $.getJSON("/req", function(data) { 
        ko.applyBindings({requests: data});
    });
});
