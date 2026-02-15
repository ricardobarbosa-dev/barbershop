window.createToast = function (text, type) {
    console.log("createToast chamada com:", text, type);

    let container = document.getElementById('toast-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const toastType = type && type.includes('error') ? 'error' : (type && type.includes('success') ? 'success' : 'warning');
    toast.className = `toast ${toastType}`;

    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${toastType === 'error' ? 'fa-times-circle' : 'fa-check-circle'}"></i>
            <span>${text}</span>
        </div>
        <i class="fas fa-times close-toast" style="cursor:pointer; opacity:0.5; padding-left:10px;"></i>
    `;

    container.appendChild(toast);

    const closeFunc = () => {
        toast.classList.add('hiding');
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, 500);
    };

    const closeBtn = toast.querySelector('.close-toast');
    if (closeBtn) closeBtn.onclick = closeFunc;

    setTimeout(closeFunc, 5000);
};

(function () {
    const initToasts = () => {
        if (typeof messages !== 'undefined' && Array.isArray(messages)) {
            messages.forEach((msg, index) => {
                setTimeout(() => {
                    window.createToast(msg.text, msg.type);
                }, index * 500);
            });
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initToasts);
    } else {
        initToasts();
    }
})();