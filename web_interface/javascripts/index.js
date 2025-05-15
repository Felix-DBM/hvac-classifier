/**
 * HVAC-Classifier - JavaScript Funktionen
 * Stellt Funktionalität für die Benutzeroberfläche bereit.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Flash Messages nach 5 Sekunden automatisch schließen
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Suchfunktion für Komponententabelle
    setupSearch();
    
    // Filter für Komponententabelle
    setupFilters();
    
    // BAS-Code Konverter
    setupCodeConverter();
    
    // Komponentendetails anzeigen
    setupComponentDetails();
    
    // Upload-Bereich Drag & Drop
    setupDragDropUpload();
});

/**
 * Richtet die Suchfunktion für die Komponententabelle ein
 */
function setupSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;
    
    searchInput.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        const table = document.querySelector('.data-table');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        updatePaginationInfo();
    });
}

/**
 * Richtet die Filter für die Komponententabelle ein
 */
function setupFilters() {
    const filterSelects = document.querySelectorAll('.filter-select');
    if (filterSelects.length === 0) return;
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            applyFilters();
        });
    });
}

/**
 * Wendet alle Filter auf die Tabelle an
 */
function applyFilters() {
    const table = document.querySelector('.data-table');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const filters = {};
    
    // Filter-Werte sammeln
    document.querySelectorAll('.filter-select').forEach(select => {
        const filterType = select.getAttribute('data-filter');
        const value = select.value;
        
        if (value && value !== 'all') {
            filters[filterType] = value;
        }
    });
    
    // Auf Zeilen anwenden
    rows.forEach(row => {
        let showRow = true;
        
        // Überprüfe jeden Filter
        for (const [filterType, filterValue] of Object.entries(filters)) {
            const cell = row.querySelector(`[data-${filterType}]`);
            if (!cell || cell.getAttribute(`data-${filterType}`) !== filterValue) {
                showRow = false;
                break;
            }
        }
        
        row.style.display = showRow ? '' : 'none';
    });
    
    updatePaginationInfo();
}

/**
 * Aktualisiert die Pagination-Informationen
 */
function updatePaginationInfo() {
    const table = document.querySelector('.data-table');
    const paginationInfo = document.querySelector('.page-info');
    if (!table || !paginationInfo) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    
    paginationInfo.textContent = `Zeige ${visibleRows.length} von ${rows.length} Komponenten`;
}

/**
 * Richtet den BAS-Code Konverter ein
 */
function setupCodeConverter() {
    const convertButton = document.getElementById('convertButton');
    if (!convertButton) return;
    
    convertButton.addEventListener('click', function() {
        const fromStandard = document.getElementById('fromStandardSelect').value;
        const toStandard = document.getElementById('toStandardSelect').value;
        const code = document.getElementById('codeInput').value.trim();
        
        if (!code) {
            showToast('Bitte geben Sie einen BAS-Code ein', 'warning');
            return;
        }
        
        // API-Anfrage senden
        fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                from_standard: fromStandard,
                to_standard: toStandard
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                document.getElementById('convertedCodeOutput').value = data.converted_code;
                showToast('Code erfolgreich konvertiert', 'success');
            }
        })
        .catch(error => {
            console.error('Konvertierungsfehler:', error);
            showToast('Fehler bei der Konvertierung', 'error');
        });
    });
    
    // Tauschen-Button-Funktionalität
    const swapButton = document.getElementById('swapStandardsButton');
    if (swapButton) {
        swapButton.addEventListener('click', function() {
            const fromSelect = document.getElementById('fromStandardSelect');
            const toSelect = document.getElementById('toStandardSelect');
            
            const tempValue = fromSelect.value;
            fromSelect.value = toSelect.value;
            toSelect.value = tempValue;
        });
    }
}

/**
 * Richtet die Funktionalität für Komponentendetails ein
 */
function setupComponentDetails() {
    // Detailansicht Modal
    const detailButtons = document.querySelectorAll('.btn-details');
    if (detailButtons.length === 0) return;
    
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const componentId = this.getAttribute('data-component-id');
            
            // API-Anfrage für Komponentendetails
            fetch(`/api/component/${componentId}`)
                .then(response => response.json())
                .then(data => {
                    // Modal mit Komponentendaten füllen
                    fillComponentModal(data);
                    
                    // Modal anzeigen
                    const componentModal = new bootstrap.Modal(document.getElementById('componentModal'));
                    componentModal.show();
                })
                .catch(error => {
                    console.error('Fehler beim Laden der Komponentendetails:', error);
                    showToast('Fehler beim Laden der Komponentendetails', 'error');
                });
        });
    });
}

/**
 * Füllt das Modal mit Komponentendaten
 */
function fillComponentModal(component) {
    const modal = document.getElementById('componentModal');
    if (!modal) return;
    
    // Grundinformationen
    modal.querySelector('.modal-title').textContent = component.element_name;
    
    // Allgemeine Informationen
    document.getElementById('component-id').textContent = component.element_id;
    document.getElementById('component-global-id').textContent = component.global_id || '-';
    document.getElementById('component-name').textContent = component.element_name;
    document.getElementById('component-class').textContent = component.element_type;
    
    // Badge für elektronisch
    const electronicBadge = document.getElementById('component-electronic');
    electronicBadge.textContent = component.is_electronic ? 'Ja' : 'Nein';
    electronicBadge.className = component.is_electronic ? 
        'badge badge-electronic' : 'badge badge-non-electronic';
    
    // BAS-Code
    document.getElementById('component-bas-code').textContent = component.bas_code || '-';
    document.getElementById('component-bas-standard').textContent = 
        (component.standard || 'amev').toUpperCase();
    
    // Standort
    const locationContainer = document.getElementById('location-info');
    if (component.location) {
        let locationHTML = '';
        
        if (component.location.storey_name) {
            locationHTML += `<div class="location-item">
                <span class="location-label">Geschoss:</span>
                <span class="location-value">${component.location.storey_name}</span>
            </div>`;
        }
        
        if (component.location.space_name) {
            locationHTML += `<div class="location-item">
                <span class="location-label">Raum:</span>
                <span class="location-value">${component.location.space_name}</span>
            </div>`;
        }
        
        locationContainer.innerHTML = locationHTML;
        locationContainer.style.display = 'block';
    } else {
        locationContainer.innerHTML = '<p>Keine Standortinformationen verfügbar</p>';
        locationContainer.style.display = 'block';
    }
    
    // Eigenschaften
    const propertiesContainer = document.getElementById('properties-container');
    if (component.properties && Object.keys(component.properties).length > 0) {
        let propertiesHTML = '';
        
        // Gruppiere Properties nach PropertySets
        const groupedProps = {};
        
        for (const [key, value] of Object.entries(component.properties)) {
            if (key.startsWith('PropertySet_')) {
                // Property Set-Name
                const psetName = key.replace('PropertySet_', '');
                if (!groupedProps[psetName]) {
                    groupedProps[psetName] = {};
                }
            } else {
                // Normale Eigenschaft - zum "Allgemein" Pset hinzufügen
                if (!groupedProps['Allgemein']) {
                    groupedProps['Allgemein'] = {};
                }
                groupedProps['Allgemein'][key] = value;
            }
        }
        
        // Property-Karten erstellen
        for (const [psetName, props] of Object.entries(groupedProps)) {
            if (Object.keys(props).length === 0) continue;
            
            propertiesHTML += `
            <div class="property-card">
                <div class="property-header">
                    <h6 class="property-title">${psetName}</h6>
                </div>
                <ul class="property-list">`;
            
            for (const [propName, propValue] of Object.entries(props)) {
                propertiesHTML += `
                <li class="property-item">
                    <span class="property-key">${propName}:</span>
                    <span class="property-value">${formatPropertyValue(propValue)}</span>
                </li>`;
            }
            
            propertiesHTML += `
                </ul>
            </div>`;
        }
        
        propertiesContainer.innerHTML = propertiesHTML;
        propertiesContainer.style.display = 'block';
    } else {
        propertiesContainer.innerHTML = '<p>Keine Eigenschaften verfügbar</p>';
        propertiesContainer.style.display = 'block';
    }
}

/**
 * Formatiert einen Eigenschaftswert für die Anzeige
 */
function formatPropertyValue(value) {
    if (value === null || value === undefined) {
        return '-';
    }
    
    if (typeof value === 'boolean') {
        return value ? 'Ja' : 'Nein';
    }
    
    if (typeof value === 'object') {
        return JSON.stringify(value);
    }
    
    return value.toString();
}

/**
 * Richtet Drag & Drop für den Upload-Bereich ein
 */
function setupDragDropUpload() {
    const dropArea = document.querySelector('.upload-area');
    if (!dropArea) return;
    
    // Verhindere Standardverhalten für Drag-Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Hervorheben beim Darüberziehen
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Dateien verarbeiten
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const fileInput = document.getElementById('fileInput');
            fileInput.files = files;
            
            // Dateinamen anzeigen
            const fileNameDisplay = document.querySelector('.file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = files[0].name;
            }
        }
    }
}

/**
 * Zeigt eine Toast-Nachricht an
 */
function showToast(message, type = 'info') {
    // Existierende Toast-Container suchen oder erstellen
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Toast-Element erstellen
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.setAttribute('id', toastId);
    
    // Toast-Inhalt
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Toast zum Container hinzufügen
    toastContainer.appendChild(toast);
    
    // Toast anzeigen
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Toast nach 5 Sekunden entfernen
    setTimeout(() => {
        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            toastElement.remove();
        }
    }, 5000);
}

