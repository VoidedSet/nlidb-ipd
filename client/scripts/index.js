// document.addEventListener('DOMContentLoaded', function() {

//     const loginLink = document.getElementById('login-link');
//     const signupLink = document.getElementById('signup-link');

//     const loginPanel = document.getElementById('login-form');
//     const signupPanel = document.getElementById('signup-form');

//     loginLink.addEventListener('click', function(){
//       signupPanel.style.display = 'none';
//       loginPanel.style.display = 'flex';
//     });

//     signupLink.addEventListener('click', function(){
//       loginPanel.style.display = 'none';
//       signupPanel.style.display = 'flex';
//     });

//     // Function to scroll down
//     const scrollToContent = () => {
//         window.scrollTo({
//             top: 850,
//             behavior: 'smooth'
//         });
//     };

//     // Set a timeout to scroll down after a delay
//     setTimeout(scrollToContent, 5000); // Adjust the delay as needed
// });

// $(document).ready(function(){
//     // Add smooth scrolling to all links
//     $("a").on('click', function(event) {
  
//       // Make sure this.hash has a value before overriding default behavior
//       if (this.hash !== "") {
//         // Prevent default anchor click behavior
//         event.preventDefault();
  
//         // Store hash
//         var hash = this.hash;
  
//         // Using jQuery's animate() method to add smooth page scroll
//         // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
//         $('html, body').animate({
//           scrollTop: $(hash).offset().top
//         }, 800, function(){
  
//           // Add hash (#) to URL when done scrolling (default click behavior)
//           window.location.hash = hash;
//         });
//       } // End if
//     });
// });


document.addEventListener("DOMContentLoaded", function () {
  const loginLink = document.getElementById("login-link");
  const signupLink = document.getElementById("signup-link");

  const loginPanel = document.getElementById("login-form");
  const signupPanel = document.getElementById("signup-form");

  // Toggle forms
  loginLink.addEventListener("click", function (e) {
    e.preventDefault();
    signupPanel.style.display = "none";
    loginPanel.style.display = "flex";
  });

  signupLink.addEventListener("click", function (e) {
    e.preventDefault();
    loginPanel.style.display = "none";
    signupPanel.style.display = "flex";
  });

  // Auto scroll after 5 seconds
  const scrollTarget = document.getElementById("target-section"); // <-- replace with your section ID
  setTimeout(() => {
    if (scrollTarget) {
      scrollTarget.scrollIntoView({ behavior: "smooth" });
    }
  }, 5000);

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({ behavior: "smooth" });
        history.pushState(null, null, "#" + targetId);
      }
    });
  });
});

