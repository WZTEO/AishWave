
    document.addEventListener("htmx:afterSwap", function () {
        const options = document.querySelectorAll(".diamond-option");
        const selectedItemInput = document.getElementById("selected-item");

        options.forEach(option => {
            option.addEventListener("click", function () {
                // Remove 'selected' class from all options
                options.forEach(opt => opt.classList.remove("active"));

                // Add 'selected' class to clicked option
                this.classList.add("active");

                // Update hidden input with selected item details
                selectedItemInput.value = JSON.stringify({
                    amount: this.dataset.amount,
                    price: this.dataset.price
                });

                console.log("Selected Item:", selectedItemInput.value);
            });
        });
    });

    function copyToClipboard(elementId) {
      const text = document.getElementById(elementId).innerText || document.getElementById(elementId).value;
      navigator.clipboard.writeText(text).then(() => {
          alert("Copied to clipboard!");
      }).catch(err => {
          console.error("Failed to copy: ", err);
      });
  }

  function toggleMenu() {
    document.getElementById('side-menu').classList.toggle('open');
    document.getElementById('menu-overlay').classList.toggle('open');
    
    // Prevent scrolling when menu is open
    document.body.style.overflow = document.body.style.overflow === 'hidden' ? '' : 'hidden';
  }


