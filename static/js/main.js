document.addEventListener('DOMContentLoaded', function() {
    // Force layout calculation and prevent shifts
    const forceReflow = document.body.offsetHeight;
    
    // Allow transitions after initial page load with a slight delay
    setTimeout(function() {
        document.documentElement.classList.remove('theme-initializing');
    }, 200);

    // Theme toggle functionality
    const themeToggle = document.querySelector('.theme-toggle');
    
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // Implement smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Store current path in session storage when navigating
    // This helps with back navigation when HTTP referrer is missing
    const currentPath = window.location.pathname;
    
    // Don't store blog post pages as referrers
    if (!currentPath.match(/^\/blog\/[^\/]+$/)) {
        sessionStorage.setItem('lastPath', currentPath);
    }
    
    // Fix back links that use referrer_url with empty value
    document.querySelectorAll('a[href=""]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const lastPath = sessionStorage.getItem('lastPath') || '/';
            window.location.href = lastPath;
        });
    });
    
    // Disable transitions when navigating away from page
    window.addEventListener('beforeunload', function() {
        document.documentElement.classList.add('theme-initializing');
    });
    
    // Pre-load theme-specific elements to prevent layout shifts
    function preloadThemeElements() {
        // Create hidden elements to force browser to calculate dimensions
        const preloadDark = document.createElement('div');
        preloadDark.style.cssText = 'position:absolute;visibility:hidden;height:0;width:0;';
        preloadDark.style.backgroundColor = 'var(--background-color)';
        document.body.appendChild(preloadDark);
        
        // Remove after computation
        setTimeout(function() {
            preloadDark.remove();
        }, 100);
    }
    
    preloadThemeElements();
});
