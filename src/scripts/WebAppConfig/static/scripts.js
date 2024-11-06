function applyFilters() {
    document.getElementById('filter-form').submit();
}

function toggleJustification(button) {
    const justification = button.nextElementSibling;
    if (justification.style.display === "none") {
        justification.style.display = "block";
        button.textContent = "AI Justification";
    } else {
        justification.style.display = "none";
        button.textContent = "AI Justification";
    }
}