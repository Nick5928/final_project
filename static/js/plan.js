$(document).ready(function() {
   
    var recipTable = $("#recip_table");

    $("#gen_meal_plan").click(function() {

        let target_calories = $("#target_cal").val();

        $.get(`api/meal_plan/${target_calories}`, function(response) {
            console.log('/api/meal_plan response: ' + JSON.stringify(response));
            create_table(response, recipTable);
        });

    });



    


});