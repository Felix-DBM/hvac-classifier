// HVAC-Classifier Main JavaScript

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.querySelector('.search-input');
    const filterSelects = document.querySelectorAll('.filter-select');
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    const paginationButtons = document.querySelectorAll('.page-btn');
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
            
            updatePaginationInfo();
        });
    }
    
    // Filter functionality
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            applyFilters();
        });
    });
    
    // Apply all active filters
    function applyFilters() {
        const activeFilters = Array.from(filterSelects)
            .filter(select => select.selectedIndex !== 0)
            .map(select => ({
                type: select.options[0].text,
                value: select.value
            }));
        
        if (activeFilters.length === 0) {
            tableRows.forEach(row => row.style.display = '');
            return;
        }
        
        tableRows.forEach(row => {
            const shouldShow = activeFilters.every(filter => {
                let cellValue;
                
                // Find the appropriate column based on filter type
                if (filter.type === 'IFC-Klasse') {
                    cellValue = row.querySelector('td:nth-child(4)').textContent;
                } else if (filter.type === 'System') {
                    cellValue = row.querySelector('td:nth-child(5)').textContent;
                }
                
                return cellValue && cellValue.includes(filter.value);
            });
            
            row.style.display = shouldShow ? '' : 'none';
        });
        
        updatePaginationInfo();
    }
    
    // Update pagination info text
    function updatePaginationInfo() {
        const visibleRows = document.querySelectorAll('.data-table tbody tr[style=""]').length;
        const totalRows = tableRows.length;
        const pageInfoElement = document.querySelector('.page-info');
        
        if (pageInfoElement) {
            if (visibleRows === totalRows) {
                pageInfoElement.textContent = `Zeige 1-${visibleRows} von ${totalRows} Komponenten`;
            } else {
                pageInfoElement.textContent = `Zeige ${visibleRows} von ${totalRows} Komponenten (gefiltert)`;
            }
        }
    }
    
    // Pagination
    paginationButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.disabled || this.classList.contains('active')) {
                return;
            }
            
            // Remove active class from all buttons
            paginationButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // You would implement actual pagination logic here
            // This is just a UI demonstration
        });
    });
    
    // Flash message auto-close
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Initialize tooltips if needed
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Modal functionality enhancements
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function (event) {
            // Get the button that triggered the modal
            const button = event.relatedTarget;
            
            // Get the row data from the parent row
            const row = button.closest('tr');
            const id = row.querySelector('.component-id').textContent;
            const name = row.querySelector('.component-name').textContent;
            const ifcClass = row.querySelector('.badge-ifc').textContent;
            const system = row.querySelector('.badge-system').textContent;
            const category = row.querySelector('.badge-category').textContent;
            
            // Update the modal content with the row data
            const modal = this;
            modal.querySelector('td.component-id').textContent = id;
            
            // Set the category in the select dropdown
            const categorySelect = modal.querySelector('#categorySelect');
            for (let i = 0; i < categorySelect.options.length; i++) {
                if (categorySelect.options[i].text === category) {
                    categorySelect.selectedIndex = i;
                    break;
                }
            }
        });
    }
});

// Handle model classification - this would connect to the backend
function classifyModel() {
    // Show loading state
    const button = document.querySelector('.btn-primary');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin btn-icon"></i> Klassifiziere...';
    button.disabled = true;
    
    // Simulate API call
    setTimeout(() => {
        // Reset button state
        button.innerHTML = originalText;
        button.disabled = false;
        
        // Show success message
        showNotification('Modell erfolgreich klassifiziert!', 'success');
    }, 2000);
    
    return false;
}

// Show notification
function showNotification(message, type = 'success') {
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${iconClass} alert-icon"></i>
            <div>
                <strong>${type === 'success' ? 'Erfolg!' : 'Fehler!'}</strong> ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const flashContainer = document.querySelector('.flash-message');
    if (flashContainer) {
        flashContainer.innerHTML = alertHtml;
        
        // Auto-close after 5 seconds
        setTimeout(() => {
            const alert = flashContainer.querySelector('.alert');
            if (alert) {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            }
        }, 5000);
    }
}