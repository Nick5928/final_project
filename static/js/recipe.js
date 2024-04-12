$(document).ready(function(){


    var recipTable = $("#recip_table");

    $("#get_recipes").click(function() {

        let ingredients = $("#ingredients").val();
        let exclude = $("#exclude").val();

        $.get(`/api/custom_recipes/${ingredients}/${exclude}`, function(response) {
            console.log('/api/custom_recipes response: ' + JSON.stringify(response));
            create_table(response, recipTable);
        });


        


    });







    

});