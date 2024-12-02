document.addEventListener('DOMContentLoaded', () => {
    const animatedBackground = document.getElementById('animated-background');
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebarClose = document.querySelector('.sidebar-close');
    const sidebar = document.querySelector('.sidebar');
    const detailsTitles = document.querySelectorAll('.details-title');
    const copyIcons = document.querySelectorAll('.copy-icon');

    // Create animated background
    for (let i = 0; i < 20; i++) {
        const square = document.createElement('div');
        square.classList.add('square');
        square.style.left = `${Math.random() * 100}%`;
        square.style.top = `${Math.random() * 100}%`;
        square.style.width = `${Math.random() * 100 + 50}px`;
        square.style.height = square.style.width;
        square.style.animationDuration = `${Math.random() * 10 + 10}s`;
        square.style.animationDelay = `${Math.random() * 5}s`;
        animatedBackground.appendChild(square);
    }

    // Themetoggle
    themeToggle.addEventListener('change', () => {
        body.classList.toggle('light');
    });

    // Sidebar toggle
    sidebarToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('active');
    });

    // Sidebar close
    sidebarClose.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar.classList.contains('active') && !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    // Smooth scrolling for sidebar links
    document.querySelectorAll('.sidebar a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('active');
                }
            }
        });
    });

    // Add this new section for sidebar dropdowns
    const sidebarDropdowns = document.querySelectorAll('.sidebar-dropdown');
    sidebarDropdowns.forEach(dropdown => {
        const menuItem = dropdown.querySelector('.sidebar-menu-item');
        menuItem.addEventListener('click', (e) => {
            e.preventDefault();
            dropdown.classList.toggle('active');
        });
    });

    // Modify the existing smooth scrolling code
    document.querySelectorAll('.sidebar-submenu a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('active');
                }
            }
        });
    });


    // Toggle details content
    detailsTitles.forEach(title => {
        title.addEventListener('click', () => {
            const content = title.nextElementSibling;
            const icon = title.querySelector('i');
            content.style.display = content.style.display === 'block' ? 'none' : 'block';
            icon.classList.toggle('bx-chevron-down');
            icon.classList.toggle('bx-chevron-up');
        });
    });

    // Copy resultto clipboard
    copyIcons.forEach(icon => {
        icon.addEventListener('click', () => {
            const resultContent = icon.closest('.result-container').querySelector('.result-content');
            navigator.clipboard.writeText(resultContent.textContent).then(() => {
                alert('Result copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    });

    // Add resize event listener
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});

// Function to toggle result visibility
function toggleResult(resultId) {
    const resultContainer = document.getElementById(resultId);
    if (resultContainer.style.display === 'none' || resultContainer.style.display === '') {
        resultContainer.style.display = 'block';
    } else {
        resultContainer.style.display = 'none';
    }
}

// Function to make API requests
async function tryItOut(inputId, errorMsgId, resultId, endpoint) {
    const input = document.getElementById(inputId);
    const errorMsg = document.getElementById(errorMsgId);
    const resultContainer = document.getElementById(resultId);
    const resultContent = resultContainer.querySelector('.result-content');
    const url = input.value.trim();

    if (!url) {
        errorMsg.textContent = 'Please enter a valid URL';
        return;
    }

    errorMsg.textContent = '';
    resultContainer.style.display = 'none';
    
    // Add loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.classList.add('loading');
    input.parentNode.appendChild(loadingIndicator);

    try {
        const response = await fetch(`https://api.ryochinel.my.id${endpoint}?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        resultContent.textContent = JSON.stringify(data, null, 2);
        resultContainer.style.display = 'block';
    } catch (error) {
        errorMsg.textContent = 'An error occurred while fetching the data. Please try again.';
        console.error('Error:', error);
    } finally {
        // Remove loading indicator
        loadingIndicator.remove();
    }
}
