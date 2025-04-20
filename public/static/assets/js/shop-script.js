// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const filterSection = document.getElementById('filterSection');
    const productCountRow = document.querySelector('.product-count-row');
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    const sortDropdown = document.getElementById('sortDropdown');
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const filterTabs = document.querySelectorAll('#filterTabs .nav-link');
    const categoryPills = document.querySelectorAll('.category-pill');
    
    // Scroll threshold values
    const COMPACT_THRESHOLD = 50;
    const HIDE_THRESHOLD = 200;
    
    // Handle scroll events
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Determine scroll direction
        const scrollingDown = scrollTop > lastScrollTop;
        
        // Apply different states based on scroll position
        if (scrollTop < COMPACT_THRESHOLD) {
            // Full view
            filterSection.classList.remove('compact', 'hidden');
            productCountRow.style.height = '30px';
            productCountRow.style.opacity = '1';
        } else if (scrollTop < HIDE_THRESHOLD) {
            // Compact view
            filterSection.classList.add('compact');
            filterSection.classList.remove('hidden');
            productCountRow.style.height = '0';
            productCountRow.style.opacity = '0';
        } else if (scrollingDown) {
            // Hidden view (only when scrolling down)
            filterSection.classList.add('hidden');
        }
        
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    }, { passive: true });

    // Toggle wishlist button heart icon
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });
    });

    // Sort dropdown functionality
    dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            dropdownItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Update dropdown button text
            sortDropdown.textContent = 'Sort By: ' + this.textContent;
        });
    });

    // Filter tabs functionality
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            filterTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
        });
    });

    // Category pills functionality
    categoryPills.forEach(pill => {
        pill.addEventListener('click', function() {
            // Toggle active state
            this.classList.toggle('active');
        });
    });
    
    // Filter button functionality
    const filterBtn = document.querySelector('.filter-btn');
    filterBtn.addEventListener('click', function() {
        // Toggle filter section visibility
        if (filterSection.classList.contains('hidden')) {
            filterSection.classList.remove('hidden');
        } else {
            filterSection.classList.add('hidden');
        }
    });
});