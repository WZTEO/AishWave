function initTournamentUI() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.section-content');

    // navButtons.forEach(button => {
    //     button.addEventListener('click', function (e) {
    //         e.preventDefault(); // 🔥 Prevent accidental reload
    //         navButtons.forEach(btn => btn.classList.remove('active'));
    //         contentSections.forEach(section => section.classList.remove('active'));

    //         this.classList.add('active');
    //         const sectionId = this.getAttribute('data-section');
    //         document.getElementById(sectionId)?.classList.add('active');
    //     });
    // });

    const stageButtons = document.querySelectorAll('.stage-btn');
    const stageContents = document.querySelectorAll('.stage-content');

    stageButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // 🔥 Prevent reload
            const selectedStage = this.getAttribute('data-stage');
            localStorage.setItem('lastTournamentStage', selectedStage);

            stageButtons.forEach(btn => btn.classList.remove('active'));
            stageContents.forEach(content => content.classList.remove('active'));

            this.classList.add('active');
            document.getElementById(selectedStage)?.classList.add('active');
        });
    });

    // Restore previous stage
    const savedStage = localStorage.getItem('lastTournamentStage');
    if (savedStage && document.getElementById(savedStage)) {
        stageButtons.forEach(btn => btn.classList.remove('active'));
        stageContents.forEach(content => content.classList.remove('active'));

        document.querySelector(`.stage-btn[data-stage="${savedStage}"]`)?.classList.add('active');
        document.getElementById(savedStage)?.classList.add('active');
    }

    // Swipe navigation
    const contentContainer = document.querySelector('.content-sections');
    let touchStartX = 0;
    let touchEndX = 0;

    if (contentContainer) {
        contentContainer.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });

        contentContainer.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            const threshold = 50;
            const activeSection = document.querySelector('.section-content.active');
            const activeNavButton = document.querySelector(`.nav-btn[data-section="${activeSection?.id}"]`);
            if (!activeNavButton) return;

            const currentIndex = [...navButtons].indexOf(activeNavButton);
            const nextIndex = touchEndX < touchStartX
                ? Math.min(currentIndex + 1, navButtons.length - 1)
                : Math.max(currentIndex - 1, 0);

            navButtons[nextIndex]?.click();
        });
    }

    // Auto-scroll nav button
    const navContainer = document.querySelector('.tournament-nav');
    navButtons.forEach(button => {
        button.addEventListener('click', function () {
            const rect = this.getBoundingClientRect();
            const navRect = navContainer.getBoundingClientRect();
            const scrollLeft = rect.left - navRect.left - (navRect.width / 2) + (rect.width / 2);
            navContainer.scrollTo({ left: scrollLeft, behavior: 'smooth' });
        });
    });

    // Auto-scroll stage button
    const stagesContainer = document.querySelector('.tournament-stages');
    if (stagesContainer) {
        stageButtons.forEach(button => {
            button.addEventListener('click', function () {
                if (window.innerWidth <= 768) {
                    const rect = this.getBoundingClientRect();
                    const contRect = stagesContainer.getBoundingClientRect();
                    const scrollLeft = rect.left - contRect.left - (contRect.width / 2) + (rect.width / 2);
                    stagesContainer.scrollTo({ left: scrollLeft, behavior: 'smooth' });
                }
            });
        });
    }

    // Match card touch feedback
    const allCards = document.querySelectorAll('.matchup-card, .squad-card, .player-row');
    allCards.forEach(card => {
        card.addEventListener('touchstart', function () {
            this.style.opacity = '0.8';
            this.style.transform = 'scale(0.98)';
        });
        card.addEventListener('touchend', function () {
            this.style.opacity = '1';
            this.style.transform = '';
        });
    });

    // Highlight fallback
    const activeButton = document.querySelector('.nav-btn.active');
    if (activeButton && window.innerWidth <= 480) {
        setTimeout(() => activeButton.click(), 100);
    }

    // Auto-scroll to active section
    setTimeout(() => {
        const activeSection = document.querySelector('.section-content.active');
        if (activeSection) {
            activeSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

document.addEventListener('DOMContentLoaded', initTournamentUI);
document.addEventListener('htmx:afterPageLoad', initTournamentUI);
