// Функции для работы с подписками
async function showSubscriptionDetails(subscriptionId) {
    try {
        const response = await fetch(`/api/subscriptions/${subscriptionId}`);
        const data = await response.json();
        
        // Показываем модальное окно с деталями
        const modal = new bootstrap.Modal(document.getElementById('subscriptionDetailsModal'));
        document.getElementById('subscriptionDetails').innerHTML = `
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>Статус:</strong> ${data.status}</p>
            <p><strong>Начало:</strong> ${new Date(data.start_date).toLocaleDateString()}</p>
            <p><strong>Конец:</strong> ${new Date(data.end_date).toLocaleDateString()}</p>
            <p><strong>Сумма:</strong> ${data.amount} руб.</p>
        `;
        modal.show();
    } catch (error) {
        console.error('Error fetching subscription details:', error);
        showAlert('Ошибка при получении деталей подписки', 'danger');
    }
}

async function extendSubscription(subscriptionId) {
    try {
        const response = await fetch(`/api/subscriptions/${subscriptionId}/extend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            showAlert('Подписка успешно продлена', 'success');
            location.reload();
        } else {
            throw new Error('Failed to extend subscription');
        }
    } catch (error) {
        console.error('Error extending subscription:', error);
        showAlert('Ошибка при продлении подписки', 'danger');
    }
}

// Функции для работы с пользователями
async function showUserDetails(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        
        // Показываем модальное окно с деталями пользователя
        const modal = new bootstrap.Modal(document.getElementById('userDetailsModal'));
        document.getElementById('userDetails').innerHTML = `
            <p><strong>ID:</strong> ${data.id}</p>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Статус:</strong> ${data.is_active ? 'Активен' : 'Неактивен'}</p>
            <p><strong>Дата регистрации:</strong> ${new Date(data.created_at).toLocaleDateString()}</p>
        `;
        modal.show();
    } catch (error) {
        console.error('Error fetching user details:', error);
        showAlert('Ошибка при получении деталей пользователя', 'danger');
    }
}

async function toggleUserStatus(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/toggle-status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            showAlert('Статус пользователя успешно изменен', 'success');
            location.reload();
        } else {
            throw new Error('Failed to toggle user status');
        }
    } catch (error) {
        console.error('Error toggling user status:', error);
        showAlert('Ошибка при изменении статуса пользователя', 'danger');
    }
}

// Вспомогательные функции
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        const container = document.createElement('div');
        container.className = 'messages';
        document.querySelector('.container').insertBefore(container, document.querySelector('.row'));
        container.appendChild(alertDiv);
    } else {
        messagesContainer.appendChild(alertDiv);
    }
    
    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация всех модальных окон
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });
    
    // Инициализация всех всплывающих подсказок
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}); 