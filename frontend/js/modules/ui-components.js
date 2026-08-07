/**
 * LawyerGrid UI Components Module
 * Provides Toast Notifications, Accessible Dialog Modals, and Skeleton Shimmer Cards.
 */

export function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <span class="toast-message">${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

export function createSkeletonCards(count = 3) {
  let html = '';
  for (let i = 0; i < count; i++) {
    html += `
      <div class="glass-card" style="padding: 24px; display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; gap: 16px; align-items: center;">
          <div class="skeleton-shimmer" style="width: 56px; height: 56px; border-radius: 50%;"></div>
          <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
            <div class="skeleton-shimmer" style="height: 20px; width: 60%;"></div>
            <div class="skeleton-shimmer" style="height: 14px; width: 40%;"></div>
          </div>
        </div>
        <div class="skeleton-shimmer" style="height: 14px; width: 90%;"></div>
        <div class="skeleton-shimmer" style="height: 14px; width: 75%;"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
          <div class="skeleton-shimmer" style="height: 24px; width: 80px;"></div>
          <div class="skeleton-shimmer" style="height: 38px; width: 120px; border-radius: 8px;"></div>
        </div>
      </div>
    `;
  }
  return html;
}

export function openModal(modalElement) {
  if (!modalElement) return;
  if (typeof modalElement.showModal === 'function') {
    modalElement.showModal();
  } else {
    modalElement.hidden = false;
  }
}

export function closeModal(modalElement) {
  if (!modalElement) return;
  if (typeof modalElement.close === 'function') {
    modalElement.close();
  } else {
    modalElement.hidden = true;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, match => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[match]));
}
