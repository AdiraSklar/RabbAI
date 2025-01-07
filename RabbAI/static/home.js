let optionCount = 1;

function increaseOptions() {
    optionCount++;
    document.getElementById("option-count").innerText = optionCount;
}

function decreaseOptions() {
    if (optionCount > 1) {
        optionCount--;
        document.getElementById("option-count").innerText = optionCount;
    }
}

function getCurrentParsha() {
    return fetch("/get_current_parsha")
        .then(response => response.json())
        .then(data => {
            let currentParsha = data.parsha;
            
            // Remove "Parashat" prefix if it exists
            if (currentParsha.startsWith("Parashat ")) {
                currentParsha = currentParsha.replace("Parashat ", "").trim();
            }

            const chooseParsha = document.getElementById("choose-parsha");

            // Set the dropdown to the current parsha
            for (let i = 0; i < chooseParsha.options.length; i++) {
                if (chooseParsha.options[i].textContent === currentParsha) {
                    chooseParsha.selectedIndex = i;
                    break;
                }
            }

            // Return the current parsha name for further use
            return currentParsha;
        })
        .catch(error => {
            console.error("Error fetching parsha:", error);
            return null; // Return null if there's an error
        });
}

// Call getCurrentParsha on page load to set the dropdown
window.onload = () => {
    getCurrentParsha();
};

// async function generateOptions() {
//     // Use await to ensure the parsha is resolved before continuing
//     const parshaName = document.getElementById("choose-parsha").value || await getCurrentParsha();
//     const audience = document.getElementById("audience").value;
//     const style = document.getElementById("style").value;
//     const names = document.getElementById("names").value;
//     const numOptions = optionCount;

//     // Debugging log to confirm data before sending
//     console.log("Parsha Name:", parshaName);
//     console.log("Audience:", audience);
//     console.log("Style Choice:", style);
//     console.log("Names Choice:", names);

//     const data = {
//         parsha_name: parshaName,
//         audience_info: audience,
//         style_choice: style,
//         names_choice: names,
//         num_options: numOptions
//     };

//     console.log("Data to be sent for generating options:", data);

//     fetch("/generate_options", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(data)
//     })
//     .then(response => {
//         if (!response.ok) throw new Error("Server error");
//         return response.json();
//     })
//     .then(data => {
//         console.log("Options data received:", data.options); // Log to verify structure
//         displayOptions(data.options);
//     })
//     .catch(error => {
//         console.error("Error generating options:", error);
//         document.getElementById("output").innerText = "An error occurred while generating options.";
//     });
// }

async function generateOptions() {
    // Show the loading spinner
    const loadingSpinner = document.getElementById("loading-spinner");
    loadingSpinner.style.display = "block";

    try {
        // Use await to ensure the parsha is resolved before continuing
        const parshaName = document.getElementById("choose-parsha").value || await getCurrentParsha();
        const audience = document.getElementById("audience").value;
        const style = document.getElementById("style").value;
        const names = document.getElementById("names").value;
        const numOptions = optionCount;

        // Debugging log to confirm data before sending
        console.log("Parsha Name:", parshaName);
        console.log("Audience:", audience);
        console.log("Style Choice:", style);
        console.log("Names Choice:", names);

        const data = {
            parsha_name: parshaName,
            audience_info: audience,
            style_choice: style,
            names_choice: names,
            num_options: numOptions
        };

        console.log("Data to be sent for generating options:", data);

        const response = await fetch("/generate_options", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Server error");

        const responseData = await response.json();
        console.log("Options data received:", responseData.options);

        // Display options in the output
        displayOptions(responseData.options);

    } catch (error) {
        console.error("Error generating options:", error);
        document.getElementById("output").innerText = "An error occurred while generating options.";
    } finally {
        // Hide the loading spinner in both success and error cases
        loadingSpinner.style.display = "none";
    }
}



function displayOptions(options) {
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = ""; // Clear previous options

    options.forEach((option, index) => {
        // Create a card element
        const optionCard = document.createElement("div");
        optionCard.className = "card option-card";
        
        // Card content
        optionCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title"> ${index + 1}: ${option.title || 'Untitled'}</h5>
                <p class="card-text">${option.description || 'No description available'}</p>
            </div>

        `;
        
        // Create a "Select" button and add styling
        const selectButton = document.createElement("button");
        selectButton.className = "select-button";
        selectButton.innerText = "Select";
        selectButton.onclick = () => selectOption(option);

        // Append the button to the card and the card to the output div
        optionCard.appendChild(selectButton);
        outputDiv.appendChild(optionCard);
    });
}


// function displayOptions(options) {
//     const outputDiv = document.getElementById("output");
//     outputDiv.innerHTML = ""; // Clear previous options

//     options.forEach((option, index) => {
//         const optionDiv = document.createElement("div");
//         optionDiv.className = "option";
        
//         // Display title and description from structured data
//         optionDiv.innerHTML = `<strong>Option ${index + 1}:</strong><br><strong>${option.title || 'Untitled'}</strong><br>${option.description || 'No description available'}`;
        
//         // Add select button for each option
//         const selectButton = document.createElement("button");
//         selectButton.innerText = "Select";
//         selectButton.onclick = () => selectOption(option);
        
//         optionDiv.appendChild(selectButton);
//         outputDiv.appendChild(optionDiv);
//     });
// }

async function selectOption(option) {
    // Show the loading overlay
    const loadingOverlay = document.getElementById("dvar-torah-loading");
    loadingOverlay.style.display = "flex"; // Show the loading spinner

    try {
        const parshaName = document.getElementById("choose-parsha").value || await getCurrentParsha();
        const audience = document.getElementById("audience").value;
        const style = document.getElementById("style").value;
        const names = document.getElementById("names").value;

        console.log("Parsha Name:", parshaName);
        console.log("Audience:", audience);
        console.log("Style Choice:", style);
        console.log("Names Choice:", names);

        const data = { 
            selected_option: option.title + ": " + option.description,
            parsha_info: `This week's parsha is Parshat ${parshaName}.`,
            audience_info: audience,
            style_choice: style,
            names_choice: names
        };

        console.log("Data to be sent for Dvar Torah generation:", data);

        const response = await fetch("/generate_dvar_torah", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error("Server error");

        const result = await response.json();
        window.location.href = `/dvar_torah?content=${encodeURIComponent(result.dvar_torah)}`;
    } catch (error) {
        console.error("Error generating Dvar Torah:", error);
    } finally {
        // Hide the loading overlay
        loadingOverlay.style.display = "none"; // Hide the loading spinner
    }
}


// async function selectOption(option) {
//     try {
//         const parshaName = document.getElementById("choose-parsha").value || await getCurrentParsha();
//         const audience = document.getElementById("audience").value;
//         const style = document.getElementById("style").value;
//         const names = document.getElementById("names").value;

//         console.log("Parsha Name:", parshaName);
//         console.log("Audience:", audience);
//         console.log("Style Choice:", style);
//         console.log("Names Choice:", names);

//         const data = { 
//             selected_option: option.title + ": " + option.description,
//             parsha_info: `This week's parsha is Parshat ${parshaName}.`,
//             audience_info: audience,
//             style_choice: style,
//             names_choice: names
//         };

//         console.log("Data to be sent for Dvar Torah generation:", data);

//         const response = await fetch("/generate_dvar_torah", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(data)
//         });

       

//         if (!response.ok) throw new Error("Server error");

//         const result = await response.json();
//         window.location.href = `/dvar_torah?content=${encodeURIComponent(result.dvar_torah)}`;
//     } catch (error) {
//         console.error("Error generating Dvar Torah:", error);
//     }
// }

function refineDvarTorah() {
    const refinement = document.getElementById("refinement")?.value;
    const content = document.getElementById("dvar-torah-content")?.innerHTML;

    console.log("Refinement:", refinement);
    console.log("Content:", content);

    if (!content) {
        console.error("Error: dvar-torah-content element is missing or empty.");
        document.getElementById("refinement-output").innerText = "Error: Dvar Torah content is missing.";
        return;
    }

    fetch("/refine_dvar_torah", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, refinement })
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error("Refinement error:", data.error);
            document.getElementById("refinement-output").innerText = "An error occurred while refining the Dvar Torah.";
        } else {
            document.getElementById("dvar-torah-content").innerHTML = data.refined_dvar_torah;
            document.getElementById("refinement-output").innerText = "Refinement applied!";
        }
    })
    .catch(error => {
        console.error("Error refining Dvar Torah:", error);
        document.getElementById("refinement-output").innerText = "An error occurred while refining the Dvar Torah.";
    });
}
