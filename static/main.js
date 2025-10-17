// Fantasy Football App JavaScript

// Add hover effects for cards
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth hover effects to navigation items
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add hover effects to cards
    const cards = document.querySelectorAll('.card, .team-card, .matchup-card, .player-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add smooth transitions for home page buttons
    const homeButtons = document.querySelectorAll('a[href^="/"]');
    homeButtons.forEach(button => {
        const buttonDiv = button.querySelector('div');
        if (buttonDiv && buttonDiv.style.background) {
            button.addEventListener('mouseenter', function() {
                buttonDiv.style.transform = 'scale(1.05)';
            });
            
            button.addEventListener('mouseleave', function() {
                buttonDiv.style.transform = 'scale(1)';
            });
        }
    });

    // Add loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const select = this.querySelector('select');
            if (select) {
                select.disabled = true;
                select.style.opacity = '0.6';
                
                // Re-enable after a delay
                setTimeout(() => {
                    select.disabled = false;
                    select.style.opacity = '1';
                }, 1000);
            }
        });
    });

    // Add table row hover effects
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
    });

    // Add click effects for interactive elements
    const clickableElements = document.querySelectorAll('.team-card, .player-card, button, select');
    clickableElements.forEach(element => {
        element.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        element.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

// Add a simple notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Slide out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}