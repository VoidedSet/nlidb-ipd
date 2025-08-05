document.addEventListener('DOMContentLoaded', function() {

    const loginLink = document.getElementById('login-link');
    const signupLink = document.getElementById('signup-link');

    const loginPanel = document.getElementById('login-form');
    const signupPanel = document.getElementById('signup-form');

    loginLink.addEventListener('click', function(){
      signupPanel.style.display = 'none';
      loginPanel.style.display = 'flex';
    });

    signupLink.addEventListener('click', function(){
      loginPanel.style.display = 'none';
      signupPanel.style.display = 'flex';
    });

    // Function to scroll down
    const scrollToContent = () => {
        window.scrollTo({
            top: 850,
            behavior: 'smooth'
        });
    };

    // Set a timeout to scroll down after a delay
    setTimeout(scrollToContent, 5000); // Adjust the delay as needed
});

$(document).ready(function(){
    // Add smooth scrolling to all links
    $("a").on('click', function(event) {
  
      // Make sure this.hash has a value before overriding default behavior
      if (this.hash !== "") {
        // Prevent default anchor click behavior
        event.preventDefault();
  
        // Store hash
        var hash = this.hash;
  
        // Using jQuery's animate() method to add smooth page scroll
        // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
        $('html, body').animate({
          scrollTop: $(hash).offset().top
        }, 800, function(){
  
          // Add hash (#) to URL when done scrolling (default click behavior)
          window.location.hash = hash;
        });
      } // End if
    });
});
