/**
 * Send a POST request to update a specific cell in the sheet.
 * @param {string} sheetName - The name of the sheet.
 * @param {number} row - The row number.
 * @param {number} col - The column number.
 */
function postCell(sheetName, row, col) {
    fetch("/post_cell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sheet_name: sheetName, row, col })
    })
    .then(res => res.json())
    .then(data => console.log("API response:", data))
    .catch(err => console.error("Error posting cell:", err));
}


/**
 * Attaches grammar check functionality to a form.
 * @param {string} formID - The ID of the form element.
 * @param {string} sheetName - The current sheet name.
 */
function requestCheckSheetGrammar(formID, sheetName) {
    const form = document.getElementById(formID);
    if (!form) {
        console.warn("Form not found:", formID);
        return;
    }

    console.log("Initializing grammar check listener...");

    form.addEventListener("submit", event => {
        event.preventDefault();

        // Open Spinner
        document.getElementById("loading-overlay").style.display = "block";
        fetch("/check_grammar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sheet_name: sheetName })
        })
        .then(res => res.json())
        .then(results => {
            console.log("Grammar results:", results);
            document.getElementById("ss").innerHTML = results.iframe;
            updateGrammarPanel(results.results);
        })
        .catch(err => console.error("Error checking grammar:", err))
        .finally(() => {
            // Turn off spinner
            document.getElementById("loading-overlay").style.display = "none";
        });
    });

    console.log("Grammar check listener attached.");
}


/**
 * Updates the grammar correction panel with given results.
 * @param {Array} correctionResults - List of grammar corrections.
 */
function updateGrammarPanel(correctionResults = []) {
    const errorList = document.getElementById("error-list");
    if (!errorList) {
        console.warn("Error list element not found.");
        return;
    }

    errorList.innerHTML = ""; // Clear previous results

    correctionResults.forEach(item => {
        const { old_value, new_value, cell } = item || {};
        if (!old_value || !new_value || !cell) {
            console.warn("Invalid grammar item:", item);
            return;
        }

        const li = document.createElement("li");
        li.innerHTML = `
            <strong>Old:</strong> ${old_value} <br>
            <strong>New:</strong> ${new_value} <br>
            <small>Cell: ${cell}</small>
            <button class="apply-btn">Apply</button>
            <button class="show-btn">Show</button>
        `;

        errorList.appendChild(li);

        li.querySelector(".apply-btn").addEventListener("click", () =>
            changeSheetCell(cell, old_value, new_value)
        );

        li.querySelector(".show-btn").addEventListener("click", () =>
            showSheetCell(cell)
        );
    });
}


/**
 * Displays a specific cell by requesting updated iframe HTML.
 * @param {string} cell - The cell identifier.
 */
function showSheetCell(cell) {
    // Turn On Spinner
    document.getElementById("loading-overlay").style.display = "block";

    fetch("/show_sheet_cell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cell })
    })
    .then(res => res.json())
    .then(results => {
        document.getElementById("ss").innerHTML = results.iframe;
    })
    .catch(err => console.error("Error showing cell:", err))
    .finally(() => {
        // Turn off Spinner
        document.getElementById("loading-overlay").style.display = "none";
    });
}


/**
 * Updates a specific cell’s value in the sheet.
 * @param {string} cell - The cell identifier.
 * @param {string} oldValue - The previous value.
 * @param {string} newValue - The new corrected value.
 */
function changeSheetCell(cell, oldValue, newValue) {
    console.log("Changing sheet value...");
    // Turn On Spinner
    document.getElementById("loading-overlay").style.display = "block";

    fetch("/change_sheet_cell", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cell, old_value: oldValue, new_value: newValue })
    })
    .then(res => res.json())
    .then(results => {
        document.getElementById("ss").innerHTML = results.iframe;
    })
    .catch(err => console.error("Error changing sheet cell:", err))
    .finally(() => {
        // Turn off Spinner
        document.getElementById("loading-overlay").style.display = "none";
        console.log("Finished updating cell.")
    });
}
