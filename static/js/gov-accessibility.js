/**
 * Government Portal Accessibility & Interaction Handler
 * Manages Font Size Scaling, High-Contrast Mode, and IST Clock.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Text Resizing Handler (Standard Gov.in feature)
    let currentFontSize = parseInt(localStorage.getItem('gov_font_size') || '16', 10);
    
    function applyFontSize(size) {
        document.documentElement.style.setProperty('--base-font-size', `${size}px`);
        localStorage.setItem('gov_font_size', size);
    }
    
    applyFontSize(currentFontSize);

    const btnDecrease = document.getElementById('btn-font-decrease');
    const btnNormal = document.getElementById('btn-font-normal');
    const btnIncrease = document.getElementById('btn-font-increase');

    if (btnDecrease) {
        btnDecrease.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentFontSize > 13) {
                currentFontSize -= 1;
                applyFontSize(currentFontSize);
            }
        });
    }

    if (btnNormal) {
        btnNormal.addEventListener('click', (e) => {
            e.preventDefault();
            currentFontSize = 16;
            applyFontSize(currentFontSize);
        });
    }

    if (btnIncrease) {
        btnIncrease.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentFontSize < 21) {
                currentFontSize += 1;
                applyFontSize(currentFontSize);
            }
        });
    }

    // 2. High Contrast Mode Toggle
    const contrastBtn = document.getElementById('btn-high-contrast');
    const isHighContrast = localStorage.getItem('gov_high_contrast') === 'true';

    if (isHighContrast) {
        document.body.classList.add('high-contrast');
    }

    if (contrastBtn) {
        contrastBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const active = document.body.classList.toggle('high-contrast');
            localStorage.setItem('gov_high_contrast', active);
        });
    }

    // 3. Indian Standard Time (IST) Live Clock
    const clockEl = document.getElementById('ist-live-clock');
    function updateClock() {
        if (!clockEl) return;
        const now = new Date();
        const options = {
            timeZone: 'Asia/Kolkata',
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        };
        const istString = new Intl.DateTimeFormat('en-IN', options).format(now);
        clockEl.textContent = `${istString} IST`;
    }
    updateClock();
    setInterval(updateClock, 1000);
});
