function postCell(sheet_name, row, col) {
    fetch("/post_cell", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sheet_name: sheet_name,
            row: row,
            col: col
        })
    })
    .then(res => res.json())
    .then(data => console.log("API response:", data))
    .catch(err => console.error("Error posting cell:", err));
}



function requestCheckSheetGrammar(formID, sheet_name) {
    const form = document.getElementById(formID);
    if (!form) {
        console.warn("Form not found:", formID);
        return;
    }
    console.log("Check grammar")
    form.addEventListener("submit", function(e) {
        e.preventDefault(); // prevent page reload
        console.log(document.getElementById("ss").innerHTML)
        fetch("/check_grammar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sheet_name: sheet_name })
        })
        .then(res => res.json())
        .then(results => { // directly use results
            console.log("Grammar results:", results);
            document.getElementById("ss").innerHTML = results.iframe;
            updateGrammarPanel(results.results)
        })
        .catch(err => console.error("Error:", err));
    });
    console.log("Finish Check Grammar")
}


function updateGrammarPanel(correction_results) {
    const errorList = document.getElementById("error-list");
    errorList.innerHTML = ""; // clear old results

    correction_results.forEach(item => {
        if (!item || !item.old_value || !item.new_value || !item.cell) {
            console.warn("Invalid grammar item", item);
            return;
        }

        const li = document.createElement("li");
        li.innerHTML = `
            <strong>Old:</strong> ${item.old_value} <br>
            <strong>New:</strong> ${item.new_value} <br>
            <small>Cell: ${item.cell}</small>
            <button class="apply-btn">Apply</button>
            <button class="show-btn">Show</button>
        `;
        errorList.appendChild(li);

        // add apply change button listener
        li.querySelector(".apply-btn").addEventListener("click", () => {
            changeSheetCell(
                item.cell,
                item.old_value,
                item.new_value
            );
        });
        li.querySelector(".show-btn").addEventListener("click", () => {
            showSheetCell(item.cell);
        });
    });
}



function showSheetCell(cell) {
    fetch("/show_sheet_cell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cell: cell })
    })
    .then(res => res.json())
    .then(results => {
        document.getElementById("ss").innerHTML = results.iframe;
    })
    .catch(err => console.error("Error:", err));
}


function changeSheetCell(cell, old_value, new_value) {
    console.log("Start Change Sheet Value")
    fetch("/change_sheet_cell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            cell: cell,
            new_value: new_value,
            old_value: old_value 
        })
    })
    .then(res => res.json())
    .then(results => {
        document.getElementById("ss").innerHTML = results.iframe;
    })
    .catch(err => console.error("Error:", err));
    console.log("Finish Change Sheet Value")
}



