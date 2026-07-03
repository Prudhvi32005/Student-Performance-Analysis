document.addEventListener('DOMContentLoaded', () => {
    // Automatically fade out flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Run Analysis Refresh Button handler
    const runAnalysisBtn = document.getElementById('run-analysis-btn');
    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', async () => {
            const originalText = runAnalysisBtn.innerHTML;
            runAnalysisBtn.disabled = true;
            runAnalysisBtn.innerHTML = `
                <svg class="animate-spin" style="width:16px;height:16px;animation:spin 1s linear infinite" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" style="opacity:0.25"></circle>
                    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Regenerating...
            `;

            try {
                const response = await fetch('/run-analysis', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (response.ok && data.status === 'success') {
                    // Show success feedback
                    showToast('success', data.message);
                    
                    // Reload after a brief delay to show new data and charts
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showToast('error', data.message || 'Failed to regenerate analysis.');
                    runAnalysisBtn.disabled = false;
                    runAnalysisBtn.innerHTML = originalText;
                }
            } catch (error) {
                showToast('error', 'Network error occurred. Check server logs.');
                runAnalysisBtn.disabled = false;
                runAnalysisBtn.innerHTML = originalText;
            }
        });
    }

    // Sidebar Toggle for Mobile Devices
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (mobileSidebarToggle && sidebar && sidebarOverlay) {
        mobileSidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            sidebarOverlay.classList.toggle('active');
        });
        
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
        });
    }

    // Interactive helper to show toast notifications
    function showToast(type, message) {
        const wrapper = document.querySelector('.main-wrapper') || document.body;
        let flashContainer = document.querySelector('.flash-messages');
        
        if (!flashContainer) {
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages';
            wrapper.insertBefore(flashContainer, wrapper.firstChild);
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <svg style="width:20px;height:20px;margin-right:8px" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                ${type === 'success' ? 
                  '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>' : 
                  '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>'}
            </svg>
            ${message}
        `;
        
        flashContainer.appendChild(alertDiv);
        
        // Auto remove
        setTimeout(() => {
            alertDiv.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alertDiv.style.opacity = '0';
            alertDiv.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                alertDiv.remove();
            }, 500);
        }, 4000);
    }
});

// Spin Animation CSS definition
const spinStyle = document.createElement('style');
spinStyle.innerHTML = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(spinStyle);

function togglePasswordVisibility(inputId, buttonEl) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const eyeOpen = buttonEl.querySelector('.eye-open');
    const eyeClosed = buttonEl.querySelector('.eye-closed');
    
    if (input.type === 'password') {
        input.type = 'text';
        if (eyeOpen) eyeOpen.style.display = 'none';
        if (eyeClosed) eyeClosed.style.display = 'block';
    } else {
        input.type = 'password';
        if (eyeOpen) eyeOpen.style.display = 'block';
        if (eyeClosed) eyeClosed.style.display = 'none';
    }
}
window.togglePasswordVisibility = togglePasswordVisibility;

