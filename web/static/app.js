// Global state
let currentOutput = {};

// Initialize tab indicator on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabIndicator();
    loadTemplateFields();
});

//Initialize and position the tab indicator
function initializeTabIndicator() {
    const indicator = document.querySelector('.tab-indicator');
    const activeTab = document.querySelector('.tab-btn.active');

    if (indicator && activeTab) {
        updateTabIndicator(activeTab);
    }
}

// Update tab indicator position
function updateTabIndicator(activeButton) {
    const indicator = document.querySelector('.tab-indicator');
    if (!indicator) return;

    const { offsetLeft, offsetWidth } = activeButton;
    indicator.style.left = `${offsetLeft + 4}px`;
    indicator.style.width = `${offsetWidth - 8}px`;
    indicator.style.top = '0.5rem';
}

// Tab management with smooth animations
function showTab(tabName) {
    const clickedButton = event.target.closest('.tab-btn');

    // Hide all tabs with fade out
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active state from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab with fade in
    const targetTab = document.getElementById(`${tabName}-tab`);
    setTimeout(() => {
        targetTab.classList.add('active');
    }, 50);

    // Set active button
    clickedButton.classList.add('active');

    // Update tab indicator position
    updateTabIndicator(clickedButton);

    // Load data for specific tabs
    if (tabName === 'dashboard') {
        loadDashboardData();
    } else if (tabName === 'templates') {
        loadTemplates();
    } else if (tabName === 'history') {
        loadHistory();
    }
}

// Form filling
const formEl = document.getElementById('fill-form');
const outEl = document.getElementById('output');
const statusEl = document.getElementById('status-message');
const previewEl = document.getElementById('field-preview');

formEl.addEventListener('submit', async (e) => {
    e.preventDefault();
    const template = document.getElementById('template-select').value;
    const prompt = document.getElementById('prompt').value;
    const useDB = document.getElementById('use-db').checked;
    const saveToDB = document.getElementById('save-to-db').checked;
    const submitBtn = formEl.querySelector('button[type="submit"]');

    if (!prompt.trim()) {
        showStatus('Please enter your trade information', 'error');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="btn-text">Processing...</span>
        <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke-width="4" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10" stroke-width="4" stroke-linecap="round"></path>
        </svg>
    `;

    showStatus('AI is analyzing your trade information...', 'info');
    previewEl.innerHTML = '<div class="loading" style="height: 100px; border-radius: 0.75rem;"></div>';
    outEl.classList.add('loading');

    try {
        const resp = await fetch('/api/fill', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template,
                prompt,
                use_db: useDB,
                save_to_db: saveToDB
            })
        });

        if (!resp.ok) {
            const errorPayload = await resp.json().catch(() => ({ error: resp.statusText }));
            throw new Error(errorPayload.error || 'Failed to fill form');
        }

        const data = await resp.json();
        currentOutput = data.filled;

        // Show success message with animation
        let message = '✓ Form filled successfully!';
        if (data.from_db) {
            message += ' (Data retrieved from database)';
        }
        showStatus(message, 'success');

        // Display in preview with stagger animation
        displayFieldPreview(data.filled);

        // Display in JSON
        outEl.classList.remove('loading');
        outEl.textContent = JSON.stringify(data.filled, null, 2);

        // Auto-hide success message after 5 seconds
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);

        // Refresh dashboard if save to DB was enabled
        if (saveToDB) {
            loadDashboardData();
        }

    } catch (err) {
        showStatus(`✕ Error: ${err.message}`, 'error');
        outEl.classList.remove('loading');
        outEl.textContent = `Error: ${err.message}`;
        previewEl.innerHTML = '';
    } finally {
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <span class="btn-text">Generate Form</span>
            <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }
});

function displayFieldPreview(fields) {
    previewEl.innerHTML = '';
    for (const [key, value] of Object.entries(fields)) {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'field-item';
        fieldDiv.innerHTML = `
            <div class="field-label">${formatLabel(key)}</div>
            <div class="field-value ${value ? '' : 'empty'}">${value || '(not filled)'}</div>
        `;
        previewEl.appendChild(fieldDiv);
    }
}

function formatLabel(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function showStatus(message, type) {
    statusEl.textContent = message;
    statusEl.className = type;
}

// Copy and download functions
function copyOutput() {
    const text = JSON.stringify(currentOutput, null, 2);
    navigator.clipboard.writeText(text).then(() => {
        showStatus('Copied to clipboard!', 'success');
        setTimeout(() => statusEl.style.display = 'none', 2000);
    }).catch(err => {
        showStatus('Failed to copy', 'error');
    });
}

function downloadOutput() {
    const text = JSON.stringify(currentOutput, null, 2);
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `filled_form_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Template management
async function loadTemplates() {
    const listEl = document.getElementById('templates-list');
    listEl.innerHTML = '<div class="loading" style="height: 100px; border-radius: 0.75rem;"></div>';

    try {
        const resp = await fetch('/api/templates');
        const data = await resp.json();

        if (data.templates && data.templates.length > 0) {
            listEl.innerHTML = '';
            data.templates.forEach((tpl, index) => {
                const div = document.createElement('div');
                div.className = 'template-item';
                div.style.animationDelay = `${index * 0.05}s`;
                div.innerHTML = `
                    <h4>${tpl.name.replace('.json', '')}</h4>
                    <div class="template-meta">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="display: inline; vertical-align: middle;">
                            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        ${tpl.fields.length} fields
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.8125rem; color: var(--text-tertiary);">${tpl.fields.slice(0, 3).join(', ')}${tpl.fields.length > 3 ? '...' : ''}</div>
                    <button onclick="viewTemplate('${tpl.name}')" class="btn-outline" style="margin-top: 1rem; width: auto; padding: 0.5rem 1rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-width="2"/>
                            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-width="2"/>
                        </svg>
                        <span>View Details</span>
                    </button>
                `;
                listEl.appendChild(div);
            });
        } else {
            listEl.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-tertiary);">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin: 0 auto 1rem; opacity: 0.5;">
                        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <p>No templates found</p>
                    <p style="font-size: 0.875rem; margin-top: 0.5rem;">Create your first template to get started</p>
                </div>
            `;
        }
    } catch (err) {
        listEl.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--error);">
                <p>Error loading templates</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">${err.message}</p>
            </div>
        `;
    }
}

async function viewTemplate(name) {
    try {
        const resp = await fetch(`/api/templates/${name}`);
        const data = await resp.json();
        alert(JSON.stringify(data.template, null, 2));
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

function showCreateTemplate() {
    document.getElementById('create-template-modal').classList.add('active');
}

function hideCreateTemplate() {
    document.getElementById('create-template-modal').classList.remove('active');
}

document.getElementById('create-template-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('template-name').value;
    const templateJson = document.getElementById('template-json').value;

    try {
        const template = JSON.parse(templateJson);
        const resp = await fetch('/api/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, template })
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error);
        }

        alert('Template created successfully!');
        hideCreateTemplate();
        loadTemplates();
        location.reload(); // Reload to update template dropdown
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
});

// History management
async function loadHistory() {
    searchHistory();
}

async function searchHistory() {
    const listEl = document.getElementById('history-list');
    const query = document.getElementById('history-search').value;

    listEl.innerHTML = '<p>Loading history...</p>';

    try {
        const resp = await fetch(`/api/history?query=${encodeURIComponent(query)}&limit=20`);

        if (!resp.ok) {
            throw new Error('Vector DB not available');
        }

        const data = await resp.json();

        if (data.history && data.history.length > 0) {
            listEl.innerHTML = '';
            data.history.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <h4>Submission</h4>
                    <div class="history-meta">Template: ${item.template} | ${new Date(item.timestamp).toLocaleString()}</div>
                    <pre>${JSON.stringify(item.data, null, 2)}</pre>
                `;
                listEl.appendChild(div);
            });
        } else {
            listEl.innerHTML = '<p>No history found.</p>';
        }
    } catch (err) {
        listEl.innerHTML = `<p>Error: ${err.message}. Make sure Vector DB is installed (pip install chromadb).</p>`;
    }
}

// Load template fields on selection
async function loadTemplateFields() {
    const templateName = document.getElementById('template-select').value;
    try {
        const resp = await fetch(`/api/templates/${templateName}`);
        const data = await resp.json();
        // Could show available fields here
    } catch (err) {
        console.error('Error loading template:', err);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTemplateFields();
    loadDashboardData();
});

// ============================================
// Dashboard Functions
// ============================================

async function loadDashboardData() {
    try {
        // Load recent history
        const resp = await fetch('/api/history?limit=10');
        if (resp.ok) {
            const data = await resp.json();
            updateDashboardStats(data.history || []);
            updateDashboardTable(data.history || []);
        }
    } catch (err) {
        console.error('Error loading dashboard:', err);
    }
}

function updateDashboardStats(history) {
    const totalForms = history.length;
    document.getElementById('stat-total-forms').textContent = totalForms;
    document.getElementById('stat-completed').textContent = totalForms;
}

function updateDashboardTable(history) {
    const tbody = document.getElementById('dashboard-table-body');

    if (!history || history.length === 0) {
        tbody.innerHTML = `
            <tr class="table-empty">
                <td colspan="5">
                    <div class="empty-state">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" stroke-width="2"/>
                        </svg>
                        <p>No recent submissions</p>
                        <p class="empty-state-sub">Submit a form to see it appear here</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = history.slice(0, 10).map((item, index) => {
        const date = new Date(item.timestamp || Date.now());
        const fieldsCount = Object.keys(item.data || {}).length;

        return `
            <tr style="animation-delay: ${index * 0.05}s">
                <td>${date.toLocaleString()}</td>
                <td><span class="table-badge">${item.template || 'Unknown'}</span></td>
                <td><span class="table-status success">Completed</span></td>
                <td>${fieldsCount} fields</td>
                <td>
                    <div class="table-actions">
                        <button onclick='viewHistoryItem(${JSON.stringify(item.data)})' class="table-action-btn">View</button>
                        <button onclick='exportHistoryItemPDF(${JSON.stringify(item)})' class="table-action-btn">PDF</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function viewHistoryItem(data) {
    alert(JSON.stringify(data, null, 2));
}

// ============================================
// Export Functions - PDF (Functional Approach)
// ============================================

// PDF Theme Configuration
const PDF_THEME = {
    colors: {
        primary: [102, 126, 234],
        text: [50, 50, 50],
        lightGray: [150, 150, 150],
        background: [248, 249, 253],
        white: [255, 255, 255]
    },
    fonts: {
        title: 24,
        subtitle: 12,
        header: 11,
        body: 10,
        small: 9,
        footer: 8
    },
    margins: { left: 20, right: 20 }
};

// Pure function to create PDF document
const createPDFDocument = () => {
    const { jsPDF } = window.jspdf;
    return new jsPDF();
};

// Pure function to add header to PDF
const addPDFHeader = (doc, title, subtitle, metaInfo = {}) => {
    // Background
    doc.setFillColor(...PDF_THEME.colors.primary);
    doc.rect(0, 0, 210, 40, 'F');

    // Title
    doc.setTextColor(...PDF_THEME.colors.white);
    doc.setFontSize(PDF_THEME.fonts.title);
    doc.setFont(undefined, 'bold');
    doc.text('Trade CRM', 20, 25);

    // Subtitle
    doc.setFontSize(PDF_THEME.fonts.subtitle);
    doc.setFont(undefined, 'normal');
    doc.text(subtitle, 20, 33);

    // Meta info (right side)
    doc.setTextColor(...PDF_THEME.colors.text);
    doc.setFontSize(PDF_THEME.fonts.body);
    let yPos = 25;
    Object.entries(metaInfo).forEach(([key, value]) => {
        doc.text(`${key}: ${value}`, 150, yPos, { align: 'right' });
        yPos += 6;
    });

    return doc;
};

// Pure function to add footer with page numbers
const addPDFFooter = (doc) => {
    const pageCount = doc.internal.getNumberOfPages();
    const pageHeight = doc.internal.pageSize.height;
    const pageWidth = doc.internal.pageSize.width;

    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(PDF_THEME.fonts.footer);
        doc.setTextColor(...PDF_THEME.colors.lightGray);
        doc.text(
            `Page ${i} of ${pageCount}`,
            pageWidth / 2,
            pageHeight - 10,
            { align: 'center' }
        );
    }

    return doc;
};

// Pure function to create table configuration
const createTableConfig = (head, body, startY = 50) => ({
    startY,
    head: [head],
    body,
    theme: 'striped',
    headStyles: {
        fillColor: PDF_THEME.colors.primary,
        fontSize: PDF_THEME.fonts.header,
        fontStyle: 'bold',
        textColor: PDF_THEME.colors.white
    },
    bodyStyles: {
        fontSize: PDF_THEME.fonts.body,
        textColor: PDF_THEME.colors.text
    },
    alternateRowStyles: {
        fillColor: PDF_THEME.colors.background
    },
    margin: PDF_THEME.margins
});

// Pure function to transform form data to table rows
const formDataToTableRows = (data) =>
    Object.entries(data).map(([key, value]) => [
        formatLabel(key),
        value || '(not filled)'
    ]);

// Pure function to transform history to summary rows
const historyToSummaryRows = (history) =>
    history.map((item, index) => {
        const date = new Date(item.timestamp || Date.now());
        return [
            index + 1,
            date.toLocaleString(),
            item.template || 'Unknown',
            `${Object.keys(item.data || {}).length} fields`
        ];
    });

// Main PDF export function (composable)
const generatePDF = ({ title, subtitle, metaInfo, tableConfig, filename }) => {
    try {
        const doc = createPDFDocument();
        addPDFHeader(doc, title, subtitle, metaInfo);
        doc.autoTable(tableConfig);
        addPDFFooter(doc);
        doc.save(filename);
        return { success: true };
    } catch (error) {
        return { success: false, error };
    }
};

// Export current form to PDF
function exportToPDF() {
    if (!currentOutput || Object.keys(currentOutput).length === 0) {
        showStatus('No data to export. Please fill a form first.', 'error');
        return;
    }

    const template = document.getElementById('template-select').value;
    const result = generatePDF({
        title: 'Trade CRM',
        subtitle: 'Form Data Export',
        metaInfo: {
            'Generated': new Date().toLocaleString(),
            'Template': template
        },
        tableConfig: createTableConfig(
            ['Field', 'Value'],
            formDataToTableRows(currentOutput)
        ),
        filename: `trade_form_${Date.now()}.pdf`
    });

    if (result.success) {
        showStatus('PDF exported successfully!', 'success');
        setTimeout(() => statusEl.style.display = 'none', 2000);
    } else {
        console.error('PDF export error:', result.error);
        showStatus('Failed to export PDF: ' + result.error.message, 'error');
    }
}

// Export single history item to PDF
function exportHistoryItemPDF(item) {
    const date = new Date(item.timestamp || Date.now());
    const result = generatePDF({
        title: 'Trade CRM',
        subtitle: 'Historical Record',
        metaInfo: {
            'Date': date.toLocaleString(),
            'Template': item.template || 'Unknown'
        },
        tableConfig: createTableConfig(
            ['Field', 'Value'],
            formDataToTableRows(item.data || {})
        ),
        filename: `trade_form_${date.getTime()}.pdf`
    });

    if (!result.success) {
        console.error('PDF export error:', result.error);
        alert('Failed to export PDF: ' + result.error.message);
    }
}

// Export history summary to PDF
function exportHistoryToPDF() {
    fetch('/api/history?limit=50')
        .then(resp => resp.json())
        .then(data => {
            const history = data.history || [];
            if (history.length === 0) {
                alert('No history data to export');
                return;
            }

            const result = generatePDF({
                title: 'Trade CRM',
                subtitle: 'History Report',
                metaInfo: {
                    'Generated': new Date().toLocaleString(),
                    'Total Records': history.length
                },
                tableConfig: createTableConfig(
                    ['#', 'Date', 'Template', 'Fields'],
                    historyToSummaryRows(history)
                ),
                filename: `trade_crm_history_${Date.now()}.pdf`
            });

            if (!result.success) {
                console.error('PDF export error:', result.error);
                alert('Failed to export PDF: ' + result.error.message);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Failed to export history: ' + err.message);
        });
}

// ============================================
// Export Functions - Excel (Functional Approach)
// ============================================

// Pure function to create workbook
const createWorkbook = () => XLSX.utils.book_new();

// Pure function to create worksheet from data
const createWorksheet = (data, columnWidths = []) => {
    const ws = XLSX.utils.json_to_sheet(data);
    if (columnWidths.length > 0) {
        ws['!cols'] = columnWidths.map(wch => ({ wch }));
    }
    return ws;
};

// Pure function to transform form data to Excel format
const formDataToExcelRows = (data) =>
    Object.entries(data).map(([key, value]) => ({
        'Field': formatLabel(key),
        'Value': value || '(not filled)'
    }));

// Pure function to create metadata sheet data
const createMetadata = (template, fieldCount) => [
    { 'Property': 'Template', 'Value': template },
    { 'Property': 'Export Date', 'Value': new Date().toLocaleString() },
    { 'Property': 'Total Fields', 'Value': fieldCount }
];

// Pure function to transform history to Excel format
const historyToExcelRows = (history) =>
    history.map((item, index) => {
        const date = new Date(item.timestamp || Date.now());
        const baseData = {
            '#': index + 1,
            'Date': date.toLocaleString(),
            'Template': item.template || 'Unknown',
            'Fields Count': Object.keys(item.data || {}).length
        };

        // Add all fields from the item
        Object.entries(item.data || {}).forEach(([key, value]) => {
            baseData[formatLabel(key)] = value || '(not filled)';
        });

        return baseData;
    });

// Pure function to create summary data
const createSummary = (history) => {
    const dateRange = history.length > 0
        ? `${new Date(history[history.length - 1].timestamp).toLocaleDateString()} - ${new Date(history[0].timestamp).toLocaleDateString()}`
        : 'N/A';

    return [
        { 'Metric': 'Total Submissions', 'Value': history.length },
        { 'Metric': 'Export Date', 'Value': new Date().toLocaleString() },
        { 'Metric': 'Date Range', 'Value': dateRange }
    ];
};

// Main Excel export function
const generateExcel = ({ sheets, filename }) => {
    try {
        const wb = createWorkbook();

        sheets.forEach(({ name, data, columnWidths }) => {
            const ws = createWorksheet(data, columnWidths);
            XLSX.utils.book_append_sheet(wb, ws, name);
        });

        XLSX.writeFile(wb, filename);
        return { success: true };
    } catch (error) {
        return { success: false, error };
    }
};

// Export current form to Excel
function exportToExcel() {
    if (!currentOutput || Object.keys(currentOutput).length === 0) {
        showStatus('No data to export. Please fill a form first.', 'error');
        return;
    }

    const template = document.getElementById('template-select').value;
    const result = generateExcel({
        sheets: [
            {
                name: 'Form Data',
                data: formDataToExcelRows(currentOutput),
                columnWidths: [30, 50]
            },
            {
                name: 'Metadata',
                data: createMetadata(template, Object.keys(currentOutput).length),
                columnWidths: [20, 40]
            }
        ],
        filename: `trade_form_${Date.now()}.xlsx`
    });

    if (result.success) {
        showStatus('Excel file exported successfully!', 'success');
        setTimeout(() => statusEl.style.display = 'none', 2000);
    } else {
        console.error('Excel export error:', result.error);
        showStatus('Failed to export Excel: ' + result.error.message, 'error');
    }
}

// Export history to Excel
function exportHistoryToExcel() {
    fetch('/api/history?limit=100')
        .then(resp => resp.json())
        .then(data => {
            const history = data.history || [];
            if (history.length === 0) {
                alert('No history data to export');
                return;
            }

            const result = generateExcel({
                sheets: [
                    {
                        name: 'History',
                        data: historyToExcelRows(history),
                        columnWidths: []
                    },
                    {
                        name: 'Summary',
                        data: createSummary(history),
                        columnWidths: [25, 40]
                    }
                ],
                filename: `trade_crm_history_${Date.now()}.xlsx`
            });

            if (!result.success) {
                console.error('Excel export error:', result.error);
                alert('Failed to export Excel: ' + result.error.message);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Failed to export history: ' + err.message);
        });
}

// Alias for exporting all data
const exportAllData = exportHistoryToExcel;
