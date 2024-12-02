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

function toggleAdvancedSearch() {
    const fields = document.getElementById('advanced-search-fields');
    fields.style.display = fields.style.display === 'none' ? 'block' : 'none';
}

// Store the scroll position before unload
window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

// Scroll to the stored position after the page loads
window.addEventListener('load', function() {
    if (localStorage.getItem('scrollPosition') !== null) {
        window.scrollTo(0, parseInt(localStorage.getItem('scrollPosition')));
        localStorage.removeItem('scrollPosition'); // Optional: Clear the stored position
    }
});

window.addEventListener('load', function() {
    if (document.getElementById('published_after').value || 
        document.getElementById('published_before').value) {
        document.getElementById('advanced-search-fields').style.display = 'block';
    }
});