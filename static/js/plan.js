$(document).ready(function() {
   
    var recipTable = $("#recip_table");

    $("#gen_meal_plan").click(function() {

        let target_calories = $("#target_cal").val();

        $.get(`/api/meal_plan/${target_calories}`, function(response) {
            console.log('/api/meal_plan response: ' + JSON.stringify(response));
            create_table(response, recipTable);
        });

    });

    

    $(document).on("click", ".recipe_add", function() {

        var row = $(this).closest("tr")

        var link = row.find(".link_cell").find("a").attr("href");
        var recipe = row.find(".link_cell").text().trim();
        var carbs = row.find(".carbs_cell").text().trim();
        var fat = row.find(".fat_cell").text().trim();
        var protein = row.find(".protein_cell").text().trim();
        var calories = row.find(".calories_cell").text().trim();


        meal_data = {
            "recipe_name": recipe,
            "recipe_link": link,
            "calories": calories,
            "fat": fat,
            "protein" : protein,
            "carbohydrates": carbs
        }

        console.log(meal_data)

        $.ajax({
            url: '/api/add_meal',
            type : 'POST',
            contentType: 'application/json',
            data: JSON.stringify(meal_data),
            success: function(response) {
                console.log(response);
            }
        })
    });



    


});
