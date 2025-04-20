document.addEventListener('DOMContentLoaded', function() {
  // Thumbnail gallery functionality
  const thumbnails = document.querySelectorAll('.thumbnail');
  const mainImage = document.getElementById('main-product-image');
  
  thumbnails.forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
      // Remove active class from all thumbnails
      thumbnails.forEach(t => t.classList.remove('active'));
      
      // Add active class to clicked thumbnail
      this.classList.add('active');
      
      // Update main image
      const imageUrl = this.getAttribute('data-image-url');
      mainImage.src = imageUrl;
    });
  });
  
  // Wishlist functionality
  const wishlistBtn = document.getElementById('add-to-wishlist');
  wishlistBtn.addEventListener('click', function() {
    const productId = this.getAttribute('data-product-id');
    
    // Toggle heart icon
    const heartIcon = this.querySelector('i');
    if (heartIcon.classList.contains('far')) {
      heartIcon.classList.remove('far');
      heartIcon.classList.add('fas');
      addToWishlist(productId);
    } else {
      heartIcon.classList.remove('fas');
      heartIcon.classList.add('far');
      removeFromWishlist(productId);
    }
  });
  
  function addToWishlist(productId) {
    // Send AJAX request to add to wishlist
    fetch('/wishlist/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        product_id: productId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showNotification('Product added to wishlist');
      }
    });
  }
  
  function removeFromWishlist(productId) {
    // Send AJAX request to remove from wishlist
    fetch('/wishlist/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        product_id: productId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showNotification('Product removed from wishlist');
      }
    });
  }
  
  // Color selection
  const colorOptions = document.querySelectorAll('.color-option');
  const selectedColorText = document.getElementById('selected-color');
  
  colorOptions.forEach(option => {
    option.addEventListener('click', function() {
      // Remove selected class from all options
      colorOptions.forEach(o => o.classList.remove('selected'));
      
      // Add selected class to clicked option
      this.classList.add('selected');
      
      // Update selected color text
      const colorName = this.getAttribute('data-color');
      selectedColorText.textContent = colorName;
    });
  });
  
  // Size selection
  const sizeOptions = document.querySelectorAll('.size-option');
  
  sizeOptions.forEach(option => {
    option.addEventListener('click', function() {
      // Remove selected class from all options
      sizeOptions.forEach(o => o.classList.remove('selected'));
      
      // Add selected class to clicked option
      this.classList.add('selected');
    });
  });
  
  // Length selection
  const lengthOptions = document.querySelectorAll('.length-option');
  
  lengthOptions.forEach(option => {
    option.addEventListener('click', function() {
      // Remove selected class from all options
      lengthOptions.forEach(o => o.classList.remove('selected'));
      
      // Add selected class to clicked option
      this.classList.add('selected');
    });
  });
  
  // Quantity selector
  const decreaseBtn = document.getElementById('decrease-quantity');
  const increaseBtn = document.getElementById('increase-quantity');
  const quantityInput = document.getElementById('quantity');
  
  decreaseBtn.addEventListener('click', function() {
    const currentValue = parseInt(quantityInput.value);
    if (currentValue > 1) {
      quantityInput.value = currentValue - 1;
    }
  });
  
  increaseBtn.addEventListener('click', function() {
    const currentValue = parseInt(quantityInput.value);
    if (currentValue < 10) {
      quantityInput.value = currentValue + 1;
    }
  });
  
  // Pincode checker
  const checkPincodeBtn = document.getElementById('check-pincode');
  const pincodeInput = document.getElementById('pincode');
  
  checkPincodeBtn.addEventListener('click', function() {
    const pincode = pincodeInput.value.trim();
    
    if (pincode.length !== 6 || isNaN(pincode)) {
      showNotification('Please enter a valid 6-digit pincode');
      return;
    }
    
    // Check delivery availability
    checkDeliveryAvailability(pincode);
  });
  
  function checkDeliveryAvailability(pincode) {
    // Send AJAX request to check delivery availability
    fetch(`/check-delivery/${pincode}/`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.available) {
        showNotification(`Delivery available to ${pincode}. Estimated delivery in ${data.days} days.`);
      } else {
        showNotification(`Sorry, delivery not available to ${pincode}.`);
      }
    });
  }
  
  // Add to bag button
  const addToBagBtn = document.getElementById('add-to-bag');
  
  addToBagBtn.addEventListener('click', function() {
    const productId = wishlistBtn.getAttribute('data-product-id');
    const quantity = quantityInput.value;
    const selectedSize = document.querySelector('.size-option.selected')?.textContent.trim();
    const selectedLength = document.querySelector('.length-option.selected')?.textContent.trim();
    const selectedColor = selectedColorText.textContent;
    
    if (!selectedSize) {
      showNotification('Please select a size');
      return;
    }
    
    if (!selectedLength) {
      showNotification('Please select a length');
      return;
    }
    
    // Add to cart
    addToCart(productId, quantity, selectedSize, selectedLength, selectedColor);
  });
  
  function addToCart(productId, quantity, size, length, color) {
    // Send AJAX request to add to cart
    fetch('/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
        size: size,
        length: length,
        color: color
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showNotification('Product added to bag');
        // Update cart count in header if needed
        updateCartCount(data.cart_count);
      } else {
        showNotification(data.message || 'Failed to add product to bag');
      }
    });
  }
  
  // Buy now button
  const buyNowBtn = document.getElementById('buy-now');
  
  buyNowBtn.addEventListener('click', function() {
    const productId = wishlistBtn.getAttribute('data-product-id');
    const quantity = quantityInput.value;
    const selectedSize = document.querySelector('.size-option.selected')?.textContent.trim();
    const selectedLength = document.querySelector('.length-option.selected')?.textContent.trim();
    const selectedColor = selectedColorText.textContent;
    
    if (!selectedSize) {
      showNotification('Please select a size');
      return;
    }
    
    if (!selectedLength) {
      showNotification('Please select a length');
      return;
    }
    
    // Add to cart and redirect to checkout
    buyNow(productId, quantity, selectedSize, selectedLength, selectedColor);
  });
  
  function buyNow(productId, quantity, size, length, color) {
    // Send AJAX request to add to cart and get checkout URL
    fetch('/cart/buy-now/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
        size: size,
        length: length,
        color: color
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Redirect to checkout
        window.location.href = data.checkout_url;
      } else {
        showNotification(data.message || 'Failed to proceed to checkout');
      }
    });
  }
  
  // Accordion functionality
  const accordionItems = document.querySelectorAll('.accordion-item');
  
  accordionItems.forEach(item => {
    const header = item.querySelector('.accordion-header');
    
    header.addEventListener('click', function() {
      // Toggle active class
      item.classList.toggle('active');
      
      // Toggle content visibility
      const content = item.querySelector('.accordion-content');
      if (item.classList.contains('active')) {
        content.style.display = 'block';
      } else {
        content.style.display = 'none';
      }
    });
  });
  
  // Helper functions
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }
  
  function updateCartCount(count) {
    // Update cart count in header if it exists
    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
      cartCountElement.textContent = count;
    }
  }
  
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
