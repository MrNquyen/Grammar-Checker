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
    const rejectList = document.getElementById("rejected-list");
    if (!errorList) {
        console.warn("Error list element not found.");
        return;
    }
    if (!rejectList) {
        console.warn("Reject list element not found.");
        return;
    }

    console.log("Updating grammar panel with results:", correctionResults);
    errorList.innerHTML = ""; // Clear previous results
    rejectList.innerHTML = ""; // Clear previous results

    correctionResults.forEach(item => {
        const { old_value, new_value, cell, is_reject } = item || {};
        if (!old_value || !new_value || !cell) {
            console.warn("Invalid grammar item:", item);
            return;
        }

        const li = document.createElement("li");
        const diff = highlightDiff(old_value, new_value);
        if ( !is_reject ) {
            console.log("Correction is Not Reject")
            li.innerHTML = `
                <div style="background:#f8f8f8; border-radius:6px; padding:8px; border:1px solid #eee; margin-bottom:8px;">
                    <div style="font-weight:bold; color:#888; margin-bottom:4px;">Old</div>
                    <div>${diff.old}</div>
                </div>
                <div style="background:#f8f8f8; border-radius:6px; padding:8px; border:1px solid #eee; margin-bottom:8px;">
                    <div style="font-weight:bold; color:#888; margin-bottom:4px;">New</div>
                    <div>${diff.new}</div>
                </div>
                <div style="margin-bottom:6px; color:#666; font-size:13px;"><small>Cell: ${cell}</small></div>
                <div style="display:flex; gap:8px;">
                    <button class="apply-btn"
                        style="background:#4caf50; color:#fff; border:none; border-radius:4px; padding:6px 16px; cursor:pointer;">Apply</button>
                    <button class="show-btn"
                        style="background:#2196f3; color:#fff; border:none; border-radius:4px; padding:6px 16px; cursor:pointer;">Show</button>
                    <button class="reject-btn"
                        style="background:#f44336; color:#fff; border:none; border-radius:4px; padding:6px 16px; cursor:pointer;">Reject</button>
                </div>
            `;
            errorList.appendChild(li);

            li.querySelector(".apply-btn").addEventListener("click", () =>
                changeSheetCell(cell, old_value, new_value)
            );

            li.querySelector(".show-btn").addEventListener("click", () =>
                showSheetCell(cell)
            );

            li.querySelector(".reject-btn").addEventListener("click", () =>
                rejectCorrection(cell)
            );
        }
        else {
            console.log("Correction is Reject")
            li.innerHTML = `
                <div style="background:#f8f8f8; border-radius:6px; padding:8px; border:1px solid #d9534f; margin-bottom:8px;">
                    <div style="font-weight:bold; color:#888; margin-bottom:4px;">Old</div>
                    <div>${diff.old}</div>
                </div>
                <div style="background:#f8f8f8; border-radius:6px; padding:8px; border:1px solid #d9534f; margin-bottom:8px;">
                    <div style="font-weight:bold; color:#888; margin-bottom:4px;">New</div>
                    <div>${diff.new}</div>
                </div>
                <div style="margin-bottom:6px; color:#666; font-size:13px;"><small>Cell: ${cell}</small></div>
                <div style="display:flex; gap:8px;">
                    <button class="allow-btn"
                        style="background:#4caf50; color:#fff; border:none; border-radius:4px; padding:6px 16px; cursor:pointer;">Undo Reject</button>
                </div>
            `;
            rejectList.appendChild(li);
            li.querySelector(".allow-btn").addEventListener("click", () =>
                allowCorrection(cell)
            );
        }
    });
}


/**
 * Displays a specific cell by requesting updated iframe HTML.
 * @param {string} cell - The cell identifier.
**/
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
 */
function changeSheetCell(cell) {
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


/**
 * Updates a specific cell’s value in the sheet.
 * @param {string} cell - The cell identifier.
 */
function rejectCorrection(cell) {
    console.log("Changing sheet value...");
    // Turn On Spinner
    document.getElementById("loading-overlay").style.display = "block";

    fetch("/set_correction_reject_status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            "cell": cell,
            "status": true
        })
    })
    .then(res => res.json())
    .then(results => {
        updateGrammarPanel(results.correction_results);
    })
    .catch(err => console.error("Error reject correction cell:", err))
    .finally(() => {
        // Turn off Spinner
        document.getElementById("loading-overlay").style.display = "none";
        console.log("Finished reject correction.")
    });
}



/**
 * Updates a specific cell’s value in the sheet.
 * @param {string} cell - The cell identifier.
 */
function allowCorrection(cell) {
    console.log("Changing sheet value...");
    // Turn On Spinner
    document.getElementById("loading-overlay").style.display = "block";

    fetch("/set_correction_reject_status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            "cell": cell,
            "status": false
        })
    })
    .then(res => res.json())
    .then(results => {
        updateGrammarPanel(results.correction_results);
    })
    .catch(err => console.error("Error reject correction cell:", err))
    .finally(() => {
        // Turn off Spinner
        document.getElementById("loading-overlay").style.display = "none";
        console.log("Finished allow correction.")
    });
}



// ============================ UTILS ===============================
/**
 * Updates a specific cell’s value in the sheet.
 * @param {string} newStr - The previous value.
 * @param {string} oldStr - The new corrected value.
 */
function highlightDiff(oldStr, newStr) {
    const oldArr = oldStr.split(' ');
    const newArr = newStr.split(' ');

    // Tìm common substring (theo từ)
    function findCommonIndices(a, b) {
        const n = a.length, m = b.length;
        const dp = Array(n + 1).fill().map(() => Array(m + 1).fill(0));
        let maxLen = 0, endA = 0, endB = 0;
        // Tìm tất cả common substring
        const commonMaskA = Array(n).fill(false);
        const commonMaskB = Array(m).fill(false);
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < m; j++) {
                if (a[i] === b[j]) {
                    dp[i + 1][j + 1] = dp[i][j] + 1;
                    // Đánh dấu là common
                    commonMaskA[i] = true;
                    commonMaskB[j] = true;
                }
            }
        }
        return { commonMaskA, commonMaskB };
    }

    const { commonMaskA, commonMaskB } = findCommonIndices(oldArr, newArr);

    // Highlight những token không phải common substring
    let resultOld = [], resultNew = [];
    for (let i = 0; i < oldArr.length; i++) {
        if (commonMaskA[i]) {
            resultOld.push(oldArr[i]);
        } else {
            resultOld.push(`<span style="background:yellow">${oldArr[i]}</span>`);
        }
    }
    for (let i = 0; i < newArr.length; i++) {
        if (commonMaskB[i]) {
            resultNew.push(newArr[i]);
        } else {
            resultNew.push(`<span style="background:yellow">${newArr[i]}</span>`);
        }
    }
    return {
        old: resultOld.join(' '),
        new: resultNew.join(' ')
    };
}