function create_table(data, recipTable) {
    for(let meal of data){
    
        let recip = meal['title']
        let carbs = meal['nutrients']['carbohydrates']
        let fat = meal['nutrients']['fat']
        let protein = meal['nutrients']['protein']
        let calories = meal['nutrients']['calories']
        let sourceURL = meal['link']

        let newRowHtml = `
        <tr>
            <td class="link_cell"><a href="${sourceURL}" target="_blank">${recip}</a></td>
            <td class = carbs_cell>${carbs}</td>
            <td class = fat_cell>${fat}</td>
            <td class = protein_cell>${protein}</td>
            <td class = calories_cell>${calories}</td>
        </tr>
    `;
        
        $(recipTable).find("tbody").append(newRowHtml);

    }
}