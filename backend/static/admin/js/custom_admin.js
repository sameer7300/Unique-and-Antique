// Custom Admin JavaScript for Unique & Antique

document.addEventListener('DOMContentLoaded', function() {
    
    // Welcome Message for New Users
    if (document.querySelector('.dashboard')) {
        setTimeout(() => {
            showNotification('Welcome to your store admin! 🎉 Need help? Check the help guide in the menu.', 'info');
        }, 2000);
    }
    
    // Auto-fill features for product forms
    if (window.location.pathname.includes('/products/product/')) {
        setupProductFormAutomation();
        setupJSONFieldHelpers();
    }
    
    // Smart notifications for common actions
    setupSmartNotifications();
    
    // Enhanced Loading States
    function showLoading(element) {
        element.innerHTML = '<span class="loading"></span> Saving your changes...';
        element.disabled = true;
    }
    
    function hideLoading(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
    
    // Auto-save indicator and Enhanced Form Submissions
    let saveTimeout;
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        // Auto-save indicator
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                
                // Show auto-save indicator
                let indicator = document.querySelector('.autosave-indicator');
                if (!indicator) {
                    indicator = document.createElement('div');
                    indicator.className = 'autosave-indicator';
                    indicator.innerHTML = '💾 Changes detected - Remember to save!';
                    indicator.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #fef3c7;
                        color: #92400e;
                        padding: 10px 15px;
                        border-radius: 6px;
                        border: 1px solid #f59e0b;
                        z-index: 9999;
                        font-size: 14px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    `;
                    document.body.appendChild(indicator);
                }
                
                // Hide after 3 seconds
                saveTimeout = setTimeout(() => {
                    if (indicator) {
                        indicator.remove();
                    }
                }, 3000);
            });
        });
        
        // Enhanced Form Submissions
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                showLoading(submitBtn);
                
                // Restore button after 3 seconds if form doesn't redirect
                setTimeout(() => {
                    if (submitBtn) {
                        hideLoading(submitBtn, originalText);
                    }
                }, 3000);
            }
        });
    });
    
    // Enhanced Table Interactions
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // Add hover effects to rows
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.01)';
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = 'none';
            });
        });
    });
    
    // Enhanced Search Functionality
    const searchInputs = document.querySelectorAll('input[type="search"], .search-form input');
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value;
            
            // Add loading indicator
            this.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'20\' height=\'20\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%2310B981\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Ccircle cx=\'11\' cy=\'11\' r=\'8\'/%3E%3Cpath d=\'m21 21-4.35-4.35\'/%3E%3C/svg%3E")';
            this.style.backgroundRepeat = 'no-repeat';
            this.style.backgroundPosition = 'right 10px center';
            this.style.paddingRight = '40px';
            
            // Debounced search
            searchTimeout = setTimeout(() => {
                if (searchTerm.length > 2) {
                    // Perform search logic here
                    console.log('Searching for:', searchTerm);
                }
            }, 500);
        });
    });
    
    // Enhanced Notifications
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}!</strong> ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">
                <span>&times;</span>
            </button>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
    
    // Enhanced Action Buttons
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Enhanced Delete Confirmations
    const deleteButtons = document.querySelectorAll('a[href*="delete"], input[value*="Delete"], button[name*="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const confirmModal = document.createElement('div');
            confirmModal.innerHTML = `
                <div class="modal-overlay" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <div class="modal-content" style="
                        background: white;
                        padding: 30px;
                        border-radius: 12px;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                        max-width: 400px;
                        text-align: center;
                    ">
                        <h3 style="color: #ef4444; margin-bottom: 20px;">Confirm Deletion</h3>
                        <p style="margin-bottom: 30px;">Are you sure you want to delete this item? This action cannot be undone.</p>
                        <div>
                            <button class="btn btn-danger confirm-delete" style="margin-right: 10px;">Yes, Delete</button>
                            <button class="btn btn-secondary cancel-delete">Cancel</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(confirmModal);
            
            confirmModal.querySelector('.confirm-delete').addEventListener('click', () => {
                if (this.tagName === 'A') {
                    window.location.href = this.href;
                } else {
                    this.form.submit();
                }
            });
            
            confirmModal.querySelector('.cancel-delete').addEventListener('click', () => {
                confirmModal.remove();
            });
            
            confirmModal.addEventListener('click', (e) => {
                if (e.target === confirmModal.querySelector('.modal-overlay')) {
                    confirmModal.remove();
                }
            });
        });
    });
    
    // Enhanced File Upload
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                const fileName = files[0].name;
                const fileSize = (files[0].size / 1024 / 1024).toFixed(2);
                
                let preview = this.parentElement.querySelector('.file-preview');
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'file-preview';
                    this.parentElement.appendChild(preview);
                }
                
                preview.innerHTML = `
                    <div style="
                        background: #f0f9ff;
                        border: 2px dashed #10B981;
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 10px;
                        text-align: center;
                    ">
                        <i class="fas fa-file-upload" style="color: #10B981; font-size: 24px; margin-bottom: 10px;"></i>
                        <p style="margin: 0; font-weight: 600;">${fileName}</p>
                        <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 14px;">${fileSize} MB</p>
                    </div>
                `;
            }
        });
    });
    
    // Enhanced Dashboard Widgets
    const widgets = document.querySelectorAll('.dashboard-widget, .card');
    widgets.forEach((widget, index) => {
        widget.style.animationDelay = `${index * 0.1}s`;
        widget.classList.add('fade-in-up');
    });
    
    // Auto-save for forms
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                const formData = new FormData(form);
                // Save to localStorage
                localStorage.setItem(`autosave_${form.id}`, JSON.stringify(Object.fromEntries(formData)));
                showNotification('Changes saved automatically', 'info');
            }, 2000));
        });
        
        // Restore from localStorage on page load
        const savedData = localStorage.getItem(`autosave_${form.id}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });
    
    // Utility function for debouncing
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Enhanced keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('input[name="_save"], button[name="_save"]');
            if (saveButton) {
                saveButton.click();
                showNotification('Saving...', 'info');
            }
        }
        
        // Ctrl+N for new item
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('a[href*="add"], .addlink');
            if (addButton) {
                window.location.href = addButton.href;
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal-overlay');
            modals.forEach(modal => modal.remove());
        }
    });
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        @keyframes ripple {
            to { transform: scale(4); opacity: 0; }
        }
        
        .notification-toast {
            animation: slideInRight 0.3s ease-out;
        }
    `;
    document.head.appendChild(style);
    
    console.log('🎨 Unique & Antique Admin Enhanced - Ready!');
});

// Global utility functions
window.UniqueAntiqueAdmin = {
    showNotification: function(message, type = 'success') {
        // Implementation moved to DOMContentLoaded for consistency
        const event = new CustomEvent('showNotification', { 
            detail: { message, type } 
        });
        document.dispatchEvent(event);
    },
    
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-PK', {
            style: 'currency',
            currency: 'PKR'
        }).format(amount);
    }
};

// 🤖 AUTOMATIC FEATURES FOR NON-IT ADMINS

function setupProductFormAutomation() {
    const titleField = document.querySelector('#id_title');
    const slugField = document.querySelector('#id_slug');
    const skuField = document.querySelector('#id_sku');
    const metaTitleField = document.querySelector('#id_meta_title');
    const metaDescField = document.querySelector('#id_meta_description');
    const descField = document.querySelector('#id_description');
    
    if (titleField) {
        // Auto-generate slug from title
        titleField.addEventListener('input', function() {
            if (slugField && !slugField.value) {
                const slug = this.value.toLowerCase()
                    .replace(/[^a-z0-9\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .trim('-');
                slugField.value = slug;
                
                // Show helpful message
                showAutoFillMessage(slugField, '🤖 Auto-generated from title');
            }
            
            // Auto-generate meta title
            if (metaTitleField && !metaTitleField.value) {
                metaTitleField.value = this.value + ' - Unique & Antique';
                showAutoFillMessage(metaTitleField, '🤖 Auto-generated SEO title');
            }
        });
    }
    
    if (descField && metaDescField) {
        // Auto-generate meta description from description
        descField.addEventListener('input', function() {
            if (!metaDescField.value && this.value.length > 10) {
                const metaDesc = this.value.substring(0, 150) + (this.value.length > 150 ? '...' : '');
                metaDescField.value = metaDesc;
                showAutoFillMessage(metaDescField, '🤖 Auto-generated from description');
            }
        });
    }
    
    // Smart stock level warnings
    const stockField = document.querySelector('#id_stock');
    if (stockField) {
        stockField.addEventListener('input', function() {
            const stock = parseInt(this.value) || 0;
            let message = '';
            let type = 'info';
            
            if (stock === 0) {
                message = '⚠️ Out of stock - product will be hidden from customers';
                type = 'warning';
            } else if (stock <= 5) {
                message = '🟡 Low stock - consider restocking soon';
                type = 'warning';
            } else if (stock <= 10) {
                message = '💡 Good stock level - you\'ll get alerts when it gets low';
                type = 'info';
            } else {
                message = '✅ Excellent stock level!';
                type = 'success';
            }
            
            showStockMessage(this, message, type);
        });
    }
    
    // Price formatting helper
    const priceField = document.querySelector('#id_price');
    if (priceField) {
        priceField.addEventListener('blur', function() {
            const price = parseFloat(this.value);
            if (price && price > 0) {
                showAutoFillMessage(this, `💰 Customer will see: PKR ${price.toLocaleString()}`);
            }
        });
    }
}

function setupSmartNotifications() {
    // Smart save notifications
    const saveButtons = document.querySelectorAll('input[name="_save"], input[name="_continue"], input[name="_addanother"]');
    saveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.name;
            let message = '';
            
            switch(action) {
                case '_save':
                    message = '💾 Saving and returning to product list...';
                    break;
                case '_continue':
                    message = '💾 Saving and staying on this page...';
                    break;
                case '_addanother':
                    message = '💾 Saving and creating another product...';
                    break;
            }
            
            if (message) {
                showNotification(message, 'info');
            }
        });
    });
    
    // Smart status change notifications
    const statusField = document.querySelector('#id_status');
    if (statusField) {
        statusField.addEventListener('change', function() {
            const status = this.value;
            let message = '';
            
            switch(status) {
                case 'active':
                    message = '✅ Product will be VISIBLE to customers on your website';
                    break;
                case 'inactive':
                    message = '⏸️ Product will be HIDDEN from customers (temporarily)';
                    break;
                case 'draft':
                    message = '📝 Product is in DRAFT mode (not visible to customers)';
                    break;
                case 'discontinued':
                    message = '🚫 Product marked as DISCONTINUED (no longer available)';
                    break;
            }
            
            if (message) {
                showStatusMessage(this, message);
            }
        });
    }
    
    // Featured product notifications
    const featuredField = document.querySelector('#id_is_featured');
    if (featuredField) {
        featuredField.addEventListener('change', function() {
            if (this.checked) {
                showNotification('⭐ Product will be FEATURED on homepage for more visibility!', 'success');
            } else {
                showNotification('📤 Product removed from featured section', 'info');
            }
        });
    }
}

function showAutoFillMessage(field, message) {
    // Remove existing message
    const existingMsg = field.parentNode.querySelector('.auto-fill-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Create new message
    const msgDiv = document.createElement('div');
    msgDiv.className = 'auto-fill-message';
    msgDiv.innerHTML = message;
    msgDiv.style.cssText = `
        background: #ecfdf5;
        color: #065f46;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 5px;
        border: 1px solid #10b981;
        animation: fadeIn 0.3s ease;
    `;
    
    field.parentNode.appendChild(msgDiv);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (msgDiv.parentNode) {
            msgDiv.remove();
        }
    }, 3000);
}

function showStockMessage(field, message, type) {
    const colors = {
        success: { bg: '#ecfdf5', color: '#065f46', border: '#10b981' },
        warning: { bg: '#fffbeb', color: '#92400e', border: '#f59e0b' },
        info: { bg: '#eff6ff', color: '#1e40af', border: '#3b82f6' }
    };
    
    // Remove existing message
    const existingMsg = field.parentNode.querySelector('.stock-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Create new message
    const msgDiv = document.createElement('div');
    msgDiv.className = 'stock-message';
    msgDiv.innerHTML = message;
    msgDiv.style.cssText = `
        background: ${colors[type].bg};
        color: ${colors[type].color};
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        margin-top: 8px;
        border: 1px solid ${colors[type].border};
        font-weight: 500;
    `;
    
    field.parentNode.appendChild(msgDiv);
}

function showStatusMessage(field, message) {
    showNotification(message, 'info');
}

function showNotification(message, type = 'info') {
    const colors = {
        success: { bg: '#ecfdf5', color: '#065f46', border: '#10b981' },
        warning: { bg: '#fffbeb', color: '#92400e', border: '#f59e0b' },
        info: { bg: '#eff6ff', color: '#1e40af', border: '#3b82f6' },
        error: { bg: '#fef2f2', color: '#991b1b', border: '#ef4444' }
    };
    
    const notification = document.createElement('div');
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type].bg};
        color: ${colors[type].color};
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid ${colors[type].border};
        z-index: 9999;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// 🎯 JSON FIELD HELPERS FOR NON-IT ADMINS

function setupJSONFieldHelpers() {
    // Add helpers for care instructions
    const careField = document.querySelector('#id_care_instructions_text');
    if (careField) {
        addJSONFieldHelper(careField, 'care_instructions', 'list');
    }
    
    // Add helpers for attributes
    const attrField = document.querySelector('#id_attributes_text');
    if (attrField) {
        addJSONFieldHelper(attrField, 'attributes', 'dict');
    }
}

function addJSONFieldHelper(textField, fieldName, type) {
    // Create preview container
    const previewContainer = document.createElement('div');
    previewContainer.className = 'json-preview-container';
    previewContainer.style.cssText = `
        margin-top: 10px;
        padding: 15px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
    `;
    
    const previewTitle = document.createElement('div');
    previewTitle.innerHTML = `<strong>🔍 Preview (what the system will save):</strong>`;
    previewTitle.style.cssText = `
        color: #495057;
        margin-bottom: 8px;
        font-family: sans-serif;
        font-size: 12px;
    `;
    
    const previewContent = document.createElement('pre');
    previewContent.style.cssText = `
        margin: 0;
        padding: 10px;
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 4px;
        color: #28a745;
        max-height: 200px;
        overflow-y: auto;
    `;
    
    previewContainer.appendChild(previewTitle);
    previewContainer.appendChild(previewContent);
    
    // Insert after the text field
    textField.parentNode.insertBefore(previewContainer, textField.nextSibling);
    
    // Update preview on input
    function updatePreview() {
        const text = textField.value.trim();
        let jsonData;
        
        if (!text) {
            jsonData = type === 'list' ? [] : {};
        } else {
            const lines = text.split('\n').map(line => line.trim()).filter(line => line);
            
            if (type === 'list') {
                jsonData = lines;
            } else {
                jsonData = {};
                lines.forEach(line => {
                    if (line.includes(':')) {
                        const [key, ...valueParts] = line.split(':');
                        jsonData[key.trim()] = valueParts.join(':').trim();
                    } else {
                        jsonData[line] = line;
                    }
                });
            }
        }
        
        previewContent.textContent = JSON.stringify(jsonData, null, 2);
        
        // Show success message
        if (text) {
            showJSONHelper(textField, `✅ ${type === 'list' ? lines.length + ' instructions' : Object.keys(jsonData).length + ' features'} will be saved`);
        }
    }
    
    // Initial preview
    updatePreview();
    
    // Update on input
    textField.addEventListener('input', updatePreview);
    
    // Add helpful examples button
    const examplesBtn = document.createElement('button');
    examplesBtn.type = 'button';
    examplesBtn.innerHTML = '💡 Show Examples';
    examplesBtn.style.cssText = `
        margin-top: 8px;
        padding: 6px 12px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
    `;
    
    examplesBtn.addEventListener('click', function() {
        let examples;
        if (type === 'list') {
            examples = `Dust with soft cloth
Avoid direct sunlight
Keep away from moisture
Use wood polish monthly
Handle with care`;
        } else {
            examples = `Material: Solid Oak Wood
Color: Rich Brown
Weight: 15 kg
Dimensions: 120cm x 80cm x 45cm
Style: Victorian
Condition: Excellent`;
        }
        
        textField.value = examples;
        updatePreview();
        showNotification('📝 Example text added! You can edit it as needed.', 'success');
    });
    
    previewContainer.appendChild(examplesBtn);
}

function showJSONHelper(field, message) {
    // Remove existing message
    const existingMsg = field.parentNode.querySelector('.json-helper-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Create new message
    const msgDiv = document.createElement('div');
    msgDiv.className = 'json-helper-message';
    msgDiv.innerHTML = message;
    msgDiv.style.cssText = `
        background: #d4edda;
        color: #155724;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 12px;
        margin-top: 5px;
        border: 1px solid #c3e6cb;
        animation: fadeIn 0.3s ease;
    `;
    
    field.parentNode.appendChild(msgDiv);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (msgDiv.parentNode) {
            msgDiv.remove();
        }
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
    
    .json-preview-container {
        transition: all 0.3s ease;
    }
    
    .json-preview-container:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
`;
document.head.appendChild(style);
