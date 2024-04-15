$(document).ready(function() {
   
    

    $(document).on("click", ".recipe_del", function() {

        var row = $(this).closest("tr")

        var link = row.find(".link_cell").find("a").attr("href");
        var recipe = row.find(".link_cell").text().trim();
        var carbs = row.find(".carbs_cell").text().trim();
        var fat = row.find(".fat_cell").text().trim();
        var protein = row.find(".protein_cell").text().trim();
        var calories = row.find(".calories_cell").text().trim();

        $.post(`/api/del_meal/${recipe}`, function(response) {
            console.log('/api/meal_plan response: ' + JSON.stringify(response));

        });
    });



    


});