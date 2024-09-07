function formatSequence(sequence, motif_type) {
    let formattedSequence = '';

    if (motif_type == 'Donor') {
        formattedSequence += sequence.substring(0, 4);
        formattedSequence += `<span class="ess-motif">${sequence.substring(4, 6)}</span>`;
        formattedSequence += sequence.substring(6, sequence.length);
    } else if (motif_type == 'Acceptor') {
        formattedSequence += sequence.substring(0, 7);
        formattedSequence += `<span class="ess-motif">${sequence.substring(7, 9)}</span>`;
        formattedSequence += sequence.substring(9, sequence.length);
    }

    return formattedSequence
}

function showError(errorMsgContainer, errorMsg) {
    errorMsgContainer.classList.remove('hide');
    errorMsgContainer.textContent = errorMsg
}

function hideError(errorMsgContainer) {
    errorMsgContainer.classList.add('hide');
    errorMsgContainer.textContent = ''
}

function getHexColorStyle(hexColor, opacity) {
    // Ensure the hex color is in the correct format (e.g., #RRGGBB)
    if (!/^#([A-Fa-f0-9]{6})$/.test(hexColor)) {
        throw new Error('Invalid hex color code.');
    }

    // Extract the red, green, and blue values from the hex color
    const red = parseInt(hexColor.slice(1, 3), 16);
    const green = parseInt(hexColor.slice(3, 5), 16);
    const blue = parseInt(hexColor.slice(5, 7), 16);

    // Create the rgba color string
    const rgbaColor = `rgba(${red}, ${green}, ${blue}, ${opacity})`;

    // Return the style string
    return `background-color: ${rgbaColor};`;
}

function cleanLoci(loci) {
    // Remove commas for easier processing
    let cleanedLocus = loci.replace(/,/g, '');
    
    // Use regex to find the format "chr<character>:<number>-<number>"
    const regex = /^chr[^\d]*(\d+)(\.\d+)?-(\d+)(\.\d+)?$/;
    const match = cleanedLocus.match(regex);

    if (match) {
        // Extract the chromosome, start and end positions
        const chr = cleanedLocus.split(':')[0];
        const start = match[1];
        const end = match[3];

        // Reconstruct the correct format without decimals
        cleanedLocus = `${chr}:${start}-${end}`;
    }

    return cleanedLocus;
}

// Function to render the NIF data in a table
function renderNifTable(data) {
    const tableDiv = document.getElementById('nifResultsTable');
    if (!data.length) {
        tableDiv.innerHTML = "<p>No data available for the selected region.</p>";
        return;
    }

    let tableHTML = `<table class="table table-bordered table-striped table-sm">
                        <thead>
                            <tr>`;
    
    // Add table headers based on keys in the first dictionary
    Object.keys(data[0]).forEach(key => {
        tableHTML += `<th>${key}</th>`;
    });
    
    tableHTML += `</tr></thead><tbody>`;
    
    // Add table rows
    data.forEach(row => {
        tableHTML += `<tr>`;
        Object.values(row).forEach(value => {
            tableHTML += `<td>${value}</td>`;
        });
        tableHTML += `</tr>`;
    });
    
    tableHTML += `</tbody></table>`;
    
    tableDiv.innerHTML = tableHTML; // Insert the table into the div
}