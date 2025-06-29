document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.section-content');
    const isMobile = window.innerWidth <= 768;

    // Handle tab switching
    function switchTab(button) {
        navButtons.forEach(btn => btn.classList.remove('active'));
        contentSections.forEach(section => section.classList.remove('active'));
        
        button.classList.add('active');
        const sectionId = button.getAttribute('data-section');
        document.getElementById(sectionId)?.classList.add('active');
        
        // Mobile-specific scroll behavior
        if (isMobile) {
            const navContainer = document.querySelector('.tournament-nav');
            if (navContainer) {
                const rect = button.getBoundingClientRect();
                const navRect = navContainer.getBoundingClientRect();
                const scrollLeft = rect.left - navRect.left - (navRect.width / 2) + (rect.width / 2);
                navContainer.scrollTo({ left: scrollLeft, behavior: 'smooth' });
            }
        }
    }

    // Different event handling for mobile vs desktop
    navButtons.forEach(button => {
        if (isMobile) {
            // Mobile - touch events with tap prevention
            let touchStartTime;
            
            button.addEventListener('touchstart', function(e) {
                touchStartTime = Date.now();
                e.preventDefault(); // Prevent any default touch behavior
            }, { passive: false });
            
            button.addEventListener('touchend', function(e) {
                // Only register as tap if under 300ms (not a swipe)
                if (Date.now() - touchStartTime < 300) {
                    e.preventDefault();
                    switchTab(this);
                }
            }, { passive: false });
        } else {
            // Desktop - regular click handler
            button.addEventListener('click', function() {
                switchTab(this);
            });
        }
    });

    // Additional mobile-only optimizations
    if (isMobile) {
        // Prevent any default touch behaviors that might cause reload
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('touchmove', function(e) {
                e.preventDefault();
            }, { passive: false });
        });

        // Add visual feedback for touches
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.96)';
            });
            btn.addEventListener('touchend', function() {
                this.style.transform = '';
            });
        });
    }
});