document.addEventListener('DOMContentLoaded', () => {
  const loginContainer = document.getElementById('login-container');
  const signupContainer = document.getElementById('signup-container');
  const loginForm = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const loaderOverlay = document.getElementById('loader-overlay');
  const authOverlay = document.getElementById('auth-overlay');
  const authTabs = document.querySelectorAll('.auth-tab');
  const authClose = document.getElementById('auth-close');
  const getStartedBtns = document.querySelectorAll('#get-started-btn, #hero-get-started, #final-cta-btn');
  const landingPage = document.getElementById('landing-page');
  const featureCards = document.querySelectorAll('.feature-card');

  // Safety check for required elements
  if (!loginContainer || !signupContainer || !loginForm || !signupForm || !loaderOverlay) {
    console.error('Required elements not found');
    return;
  }

  // Function to show loader
  const showLoader = () => {
    loaderOverlay.style.display = 'flex';
  };

  // Function to hide loader
  const hideLoader = () => {
    loaderOverlay.style.display = 'none';
  };

  // Function to open auth modal
  const openAuthModal = () => {
    authOverlay.classList.add('visible');
    document.body.style.overflow = 'hidden'; // Prevent scrolling
  };

  // Function to close auth modal
  const closeAuthModal = () => {
    authOverlay.classList.remove('visible');
    document.body.style.overflow = ''; // Enable scrolling
  };

  // Auth tab handling
  authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.getAttribute('data-tab');
      
      // Update active tab
      authTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Show corresponding form
      if (tabId === 'login') {
        loginContainer.style.display = 'block';
        signupContainer.style.display = 'none';
      } else {
        loginContainer.style.display = 'none';
        signupContainer.style.display = 'block';
      }
    });
  });

  // Close auth modal
  if (authClose) {
    authClose.addEventListener('click', closeAuthModal);
  }

  // Close modal when clicking outside
  authOverlay.addEventListener('click', (e) => {
    if (e.target === authOverlay) {
      closeAuthModal();
    }
  });

  // Open auth modal when Get Started button is clicked
  getStartedBtns.forEach(btn => {
    btn.addEventListener('click', openAuthModal);
  });

  // Simulate loading time (remove in production and replace with actual API calls)
  const simulateLoading = async () => {
    showLoader();
    await new Promise(resolve => setTimeout(resolve, 2000));
    hideLoader();
  };

  // Toggle between login and signup
  document.querySelectorAll('.agreement a').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      loginContainer.style.display = loginContainer.style.display === 'none' ? 'block' : 'none';
      signupContainer.style.display = signupContainer.style.display === 'none' ? 'block' : 'none';
    });
  });

  // Modified login/signup handlers to transition to finance interface
  const showFinanceInterface = async () => {
    await simulateLoading();
    closeAuthModal();
    landingPage.style.display = 'none';
    const financeInterface = document.getElementById('finance-interface');
    financeInterface.style.display = 'flex';
  };

  // Modify login form submission
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = loginForm.querySelector('input[type="email"]').value;
    const password = loginForm.querySelector('input[type="password"]').value;
    
    // Simulate authentication
    await showFinanceInterface();
  });

  // Modify signup form submission
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm').value;

    if (password !== confirmPassword) {
      alert("Passwords don't match!");
      return;
    }

    // Simulate authentication
    await showFinanceInterface();
  });

  // Feature cards animation on scroll
  const animateOnScroll = () => {
    featureCards.forEach(card => {
      const cardPosition = card.getBoundingClientRect().top;
      const screenPosition = window.innerHeight / 1.3;
      
      if (cardPosition < screenPosition) {
        card.classList.add('visible');
      }
    });
  };

  // Run once on load
  animateOnScroll();
  
  // Add scroll event listener
  window.addEventListener('scroll', animateOnScroll);

  // Global state to track user's balance and investments
  let userState = {
    balance: 10000.00,
    investments: {
      quick: null,  
      premium: null 
    }
  };

  // Function to format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  // Function to update balance display
  const updateBalanceDisplay = () => {
    const balanceDisplay = document.querySelector('.balance-card h1');
    balanceDisplay.textContent = formatCurrency(userState.balance);
  };

  // Function to format countdown time
  const formatCountdown = (timeLeftInSeconds) => {
    const days = Math.floor(timeLeftInSeconds / (24 * 60 * 60));
    const hours = Math.floor((timeLeftInSeconds % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((timeLeftInSeconds % (60 * 60)) / 60);
    return `${days}d ${hours.toString().padStart(2, '0')}h ${minutes.toString().padStart(2, '0')}m`;
  };

  // Function to create and manage investment countdown
  const createInvestmentCountdown = (investment) => {
    const countdownEl = document.createElement('div');
    countdownEl.classList.add('investment-countdown');
  
    const titleEl = document.createElement('div');
    titleEl.classList.add('countdown-title');
    titleEl.textContent = `Investment: ${formatCurrency(investment.amount)}`;
  
    const timeEl = document.createElement('div');
    timeEl.classList.add('countdown-time');
  
    const returnsEl = document.createElement('div');
    returnsEl.classList.add('countdown-returns');
  
    countdownEl.appendChild(titleEl);
    countdownEl.appendChild(timeEl);
    countdownEl.appendChild(returnsEl);
  
    // Insert countdown into the appropriate padlock card
    const padlockCard = document.querySelector(
      investment.type === 'quick' ? '.padlock-card:first-child' : '.padlock-card:last-child'
    );
    if (padlockCard) {
      padlockCard.appendChild(countdownEl);
    }
  
    // Start countdown
    const endTime = investment.endTime;
  
    const updateCountdown = () => {
      const now = Math.floor(Date.now() / 1000);
      const timeLeft = endTime - now;
      
      if (timeLeft <= 0) {
        // Investment completed
        if (countdownEl) {
          countdownEl.remove();
        }
        const returns = investment.amount * (1 + (investment.dailyReturn * investment.duration / 100));
        userState.balance += returns;
        updateBalanceDisplay();
        
        // Clear the investment slot
        userState.investments[investment.type] = null;
        
        // Clear the interval
        if (investment.countdownInterval) {
          clearInterval(investment.countdownInterval);
        }
        
        alert(`Investment completed! You received ${formatCurrency(returns)}`);
        return;
      }
      
      timeEl.textContent = formatCountdown(timeLeft);
      const earnedSoFar = investment.amount * (investment.dailyReturn / 100) * 
        ((investment.duration * 24 * 60 * 60 - timeLeft) / (24 * 60 * 60));
      returnsEl.textContent = `Earned so far: ${formatCurrency(earnedSoFar)}`;
    };
  
    updateCountdown();
    const countdownInterval = setInterval(updateCountdown, 60000); // Update every minute
  
    return countdownInterval;
  };

  // Enhanced navigation button handling
  const navButtons = document.querySelectorAll('.nav-btn');

  navButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      // Remove active class from all buttons
      navButtons.forEach(b => b.classList.remove('active'));
      
      // Add active class to clicked button
      this.classList.add('active');
      
      // Create ripple effect
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
      
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
      
      // Handle navigation based on button text
      const pageName = this.querySelector('span').textContent;
      
      if(pageName === 'Store') {
        // Show store interface
        document.getElementById('finance-interface').style.display = 'none';
        document.getElementById('shop-interface').style.display = 'flex';
      } else if(pageName === 'Tourn') {
        // Hide all possible interfaces without showing any specific feature
        const interfaces = [
          'profile-interface',
          'referral-interface',
          'investment-interface',
          'contact-interface',
          'stocks-interface',
          'tasks-interface',
          'shop-interface',
          'finance-interface'
        ];
        
        interfaces.forEach(id => {
          const element = document.getElementById(id);
          if (element) {
            element.classList.remove('open');
            element.style.display = 'none';
          }
        });
        
        // Optionally, you can add a simple placeholder or do nothing
        console.log('Tournament section clicked - no features available');
      } else if(pageName === 'Home') {
        // Show finance interface
        document.getElementById('shop-interface').style.display = 'none';
        document.getElementById('finance-interface').style.display = 'flex';
      } else if(pageName === 'Invest') {
        // Show investment interface
        if (investmentInterface) {
          investmentInterface.classList.add('open');
        }
      }
    });
  });

  // Prevent context menu on navigation buttons
  document.querySelector('.bottom-nav').addEventListener('contextmenu', (e) => {
    e.preventDefault();
  });

  // Handle investment buttons
  document.querySelectorAll('.invest-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const padlockCard = btn.closest('.padlock-card');
      const input = padlockCard.querySelector('input');
      const amount = parseFloat(input.value);
      const isQuickPlan = padlockCard === document.querySelector('.padlock-card:first-child');
      
      const minAmount = parseFloat(input.min);
      const maxAmount = parseFloat(input.max);
      
      // Validate amount
      if (!amount || amount < minAmount || amount > maxAmount) {
        alert(`Please enter an amount between ${formatCurrency(minAmount)} and ${formatCurrency(maxAmount)}`);
        return;
      }
      
      // Check balance
      if (amount > userState.balance) {
        alert('Insufficient balance for this investment');
        return;
      }
      
      // Check if plan is already locked
      const planType = isQuickPlan ? 'quick' : 'premium';
      if (userState.investments[planType]) {
        alert(`You already have an active ${isQuickPlan ? 'Quick Returns' : 'Premium Returns'} Plan. Please wait for it to complete before starting a new one.`);
        return;
      }
      
      // Create investment object
      const investment = {
        id: Date.now(),
        amount: amount,
        duration: isQuickPlan ? 31 : 61,
        dailyReturn: isQuickPlan ? 4 : 3,
        startTime: Math.floor(Date.now() / 1000),
        endTime: Math.floor(Date.now() / 1000) + (isQuickPlan ? 31 : 61) * 24 * 60 * 60,
        type: planType
      };
      
      // Deduct amount from balance
      userState.balance -= amount;
      updateBalanceDisplay();
      
      // Add to active investments
      userState.investments[planType] = investment;
      
      // Create countdown
      const countdownInterval = createInvestmentCountdown(investment);
      
      // Store interval for cleanup
      investment.countdownInterval = countdownInterval;
      
      // Show success message
      alert(`Successfully locked ${formatCurrency(amount)} for ${investment.duration} days!`);
      
      // Clear input
      input.value = '';
    });
  });

  // Action buttons handling
  document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
      const isDeposit = this.classList.contains('deposit');
      const amount = isDeposit ? 500 : -200; // Example amounts
      
      if (!isDeposit && Math.abs(amount) > userState.balance) {
        alert('Insufficient balance');
        return;
      }
      
      showLoader();
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      userState.balance += amount;
      updateBalanceDisplay();
      
      addTransactionToHistory({
        title: isDeposit ? 'Deposit' : 'Withdrawal',
        amount: amount
      });
      
      hideLoader();
      alert(`${isDeposit ? 'Deposit' : 'Withdrawal'} successful!`);
    });
  });

  document.querySelectorAll('.secondary-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
      
      const action = this.textContent.trim();
      console.log(`${action} button clicked`);
      // You can add specific functionality for each button here
    });
  });

  // Handle social login buttons
  document.querySelectorAll('.social-button').forEach(button => {
    button.addEventListener('click', async (e) => {
      const platform = e.currentTarget.classList[1];
      await simulateLoading();
      console.log(`${platform} login clicked`);
      // Add your social login logic here
    });
  });

  // Handle forgot password
  document.getElementById('forgot-link').addEventListener('click', async (e) => {
    e.preventDefault();
    await simulateLoading();
    // Add your forgot password logic here
    console.log('Forgot password clicked');
  });

  // Menu handling
  const menuBtn = document.querySelector('.menu-btn');
  const menuClose = document.getElementById('menu-close');
  const sideMenu = document.getElementById('side-menu');
  const menuOverlay = document.getElementById('menu-overlay');

  function openMenu() {
    sideMenu.classList.add('open');
    menuOverlay.classList.add('open');
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    sideMenu.classList.remove('open');
    menuOverlay.classList.remove('open');
    // Restore body scrolling
    document.body.style.overflow = '';
  }

  menuBtn.addEventListener('click', openMenu);
  if (menuClose) {
    menuClose.addEventListener('click', closeMenu);
  }
  if (menuOverlay) {
    menuOverlay.addEventListener('click', closeMenu);
  }

  // Enhanced menu item click handling with social icons toggle
  document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function(e) {
      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
      
      const action = this.querySelector('.text').textContent.trim();
      console.log(`${action} clicked`);
      
      // Handle specific menu item clicks
      if (action === 'Tournament') {
        showTournamentModal();
        e.stopPropagation();
        return; // Don't close menu when showing tournament modal
      }

      if (action === 'Contact Us') {
        const contactInterface = document.getElementById('contact-interface');
        if (contactInterface) {
          contactInterface.classList.add('open');
        }
        e.stopPropagation();
      }
      
      if (action === 'Referrals') {
        const referralInterface = document.getElementById('referral-interface');
        if (referralInterface) {
          referralInterface.classList.add('open');
        }
        e.stopPropagation();
        return; // Don't close menu when opening referral interface
      }
      
      if (action === 'Profile') {
        const profileInterface = document.getElementById('profile-interface');
        if (profileInterface) {
          profileInterface.classList.add('open');
        }
        e.stopPropagation();
        return; // Don't close menu when opening profile interface
      }
      
      // Handle Follow Us button click
      if (this.classList.contains('follow-us-btn')) {
        const socialIcons = document.querySelector('.social-icons');
        if (socialIcons) {
          if (socialIcons.style.display === 'none' || socialIcons.style.display === '') {
            socialIcons.style.display = 'grid';
          } else {
            socialIcons.style.display = 'none';
          }
        }
        return; // Don't close menu when toggling social icons
      }
      
      // Close menu for other items
      closeMenu();
    });
  });

  // Add click handlers for social media links
  document.querySelectorAll('.social-link').forEach(link => {
    link.addEventListener('click', (e) => {
      // Don't prevent default to allow the link to open
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
      const platform = link.classList[1];
      console.log(`Opening ${platform} profile...`);
    });
  });

  // Handle touch swipe to close menu
  let touchStartX = 0;
  let touchEndX = 0;

  if (sideMenu) {
    sideMenu.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    }, false);

    sideMenu.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, false);

    function handleSwipe() {
      if (touchEndX < touchStartX && touchStartX - touchEndX > 50) {
        closeMenu();
      }
    }
  }

  // Remove existing menu button click handler
  const oldMenuBtnHandler = menuBtn.onclick;
  menuBtn.onclick = null;

  // Add shop functionality
  const shopBtn = document.querySelector('.shop-btn');
  const backBtn = document.querySelector('.back-btn');
  const shopInterface = document.getElementById('shop-interface');
  const financeInterface = document.getElementById('finance-interface');

  if (shopBtn && backBtn && shopInterface && financeInterface) {
    shopBtn.addEventListener('click', () => {
      financeInterface.style.display = 'none';
      shopInterface.style.display = 'flex';
    });

    backBtn.addEventListener('click', () => {
      shopInterface.style.display = 'none';
      financeInterface.style.display = 'flex';
    });
  }

  // Add product card hover effect
  document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', () => {
      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
      
      // Placeholder for product details view
      console.log('Product clicked');
    });
  });

  // Prevent context menu on top navigation
  document.querySelector('.top-nav').addEventListener('contextmenu', (e) => {
    e.preventDefault();
  });

  // Contact form handling
  const contactInterface = document.getElementById('contact-interface');
  const contactClose = document.getElementById('contact-close');
  const contactForm = document.getElementById('contact-form');

  // Show contact form when Contact Us is clicked
  // document.querySelector('.menu-item:nth-child(2)').addEventListener('click', function() {
  //   contactInterface.classList.add('open');
  //   // Don't close the menu when opening contact form
  //   event.stopPropagation();
  // });

  if (contactClose) {
    contactClose.addEventListener('click', () => {
      contactInterface.classList.remove('open');
    });
  }

  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      // Show loader
      showLoader();
      
      // Simulate form submission
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Hide loader
      hideLoader();
      
      // Clear form
      contactForm.reset();
      
      // Close contact interface
      if (contactInterface) {
        contactInterface.classList.remove('open');
      }
      
      // Close menu
      closeMenu();
      
      // Show success message
      alert('Message sent successfully!');
    });
  }

  if (contactInterface) {
    contactInterface.addEventListener('click', (e) => {
      if (e.target === contactInterface) {
        contactInterface.classList.remove('open');
      }
    });
  }

  // Profile interface handling
  const profileInterface = document.getElementById('profile-interface');
  const profileClose = document.getElementById('profile-close');
  const profileButton = document.querySelector('.nav-btn:last-child');
  const logoutBtn = document.querySelector('.logout-btn');

  if (profileButton) {
    profileButton.addEventListener('click', () => {
      if (profileInterface) {
        profileInterface.classList.add('open');
      }
    });
  }

  if (profileClose) {
    profileClose.addEventListener('click', () => {
      profileInterface.classList.remove('open');
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      showLoader();
      await new Promise(resolve => setTimeout(resolve, 1500));
      hideLoader();
      // Return to login page
      document.getElementById('finance-interface').style.display = 'none';
      document.getElementById('auth-container').style.display = 'flex';
      if (profileInterface) {
        profileInterface.classList.remove('open');
      }
    });
  }

  if (profileInterface) {
    profileInterface.addEventListener('click', (e) => {
      if (e.target === profileInterface) {
        profileInterface.classList.remove('open');
      }
    });
  }

  const referralInterface = document.getElementById('referral-interface');
  const referralButton = document.querySelector('.nav-btn:nth-child(3)');
  const referralClose = document.getElementById('referral-close');
  const copyButton = document.querySelector('.copy-btn');

  if (referralButton) {
    referralButton.addEventListener('click', () => {
      if (referralInterface) {
        referralInterface.classList.add('open');
      }
    });
  }

  if (referralClose) {
    referralClose.addEventListener('click', () => {
      referralInterface.classList.remove('open');
    });
  }

  if (referralInterface) {
    referralInterface.addEventListener('click', (e) => {
      if (e.target === referralInterface) {
        referralInterface.classList.remove('open');
      }
    });
  }

  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const codeDisplay = document.querySelector('.code-display');
      const code = codeDisplay.textContent;
      
      try {
        await navigator.clipboard.writeText(code);
        copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
          copyButton.innerHTML = '<i class="far fa-copy"></i> Copy';
        }, 2000);
        
        // Add haptic feedback if available
        if (window.navigator.vibrate) {
          window.navigator.vibrate(50);
        }
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    });
  }

  const investmentInterface = document.getElementById('investment-interface');
  const investmentClose = document.getElementById('investment-close');
  const investButton = document.querySelector('.nav-btn:nth-child(2)');

  if (investButton) {
    investButton.addEventListener('click', () => {
      if (investmentInterface) {
        investmentInterface.classList.add('open');
      }
    });
  }

  if (investmentClose) {
    investmentClose.addEventListener('click', () => {
      investmentInterface.classList.remove('open');
    });
  }

  if (investmentInterface) {
    investmentInterface.addEventListener('click', (e) => {
      if (e.target === investmentInterface) {
        investmentInterface.classList.remove('open');
      }
    });
  }

  // Add input validation and formatting
  document.querySelectorAll('.investment-input input').forEach(input => {
    input.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      const min = parseFloat(e.target.min);
      const max = parseFloat(e.target.max);
      
      // Remove invalid class initially
      input.classList.remove('invalid');
      
      // Validate input
      if (value < min || value > max) {
        input.classList.add('invalid');
        // Optional: add vibration feedback on mobile
        if (window.navigator.vibrate) {
          window.navigator.vibrate(50);
        }
      }
      
      // Format number to 2 decimal places if needed
      if (value && !Number.isInteger(value)) {
        e.target.value = parseFloat(value.toFixed(2));
      }
    });
    
    // Add focus animation
    input.addEventListener('focus', () => {
      input.closest('.input-wrapper').style.transform = 'scale(1.02)';
    });
    
    input.addEventListener('blur', () => {
      input.closest('.input-wrapper').style.transform = 'scale(1)';
    });
  });

  // Product detail handling
  const productDetailInterface = document.getElementById('product-detail-interface');
  const productDetailClose = document.getElementById('product-detail-close');
  const freeFireCard = document.querySelector('.product-card:first-child');
  const productDetailForm = document.getElementById('product-detail-form');

  if (freeFireCard) {
    freeFireCard.addEventListener('click', () => {
      productDetailInterface.classList.add('open');
    });
  }

  if (productDetailClose) {
    productDetailClose.addEventListener('click', () => {
      // Reset form
      productDetailForm.reset();
      // Remove active class from all options
      const diamondOptions = document.querySelectorAll('.diamond-option');
      diamondOptions.forEach(opt => opt.classList.remove('active'));
      let selectedOption = null;
      // Close interface
      productDetailInterface.classList.remove('open');
    });
  }

  if (productDetailInterface) {
    productDetailInterface.addEventListener('click', (e) => {
      if (e.target === productDetailInterface) {
        // Reset form
        productDetailForm.reset();
        // Remove active class from all options
        const diamondOptions = document.querySelectorAll('.diamond-option');
        diamondOptions.forEach(opt => opt.classList.remove('active'));
        let selectedOption = null;
        // Close interface
        productDetailInterface.classList.remove('open');
      }
    });
  }

  const diamondOptions = document.querySelectorAll('.diamond-option');
  let selectedOption = null;

  diamondOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      diamondOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  if (productDetailForm) {
    productDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedOption) {
        alert('Please select a diamond package');
        return;
      }

      const playerId = document.getElementById('player-id').value;
      if (!playerId) {
        alert('Please enter your Player ID');
        return;
      }

      // Get price from selected option
      const priceText = selectedOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful!');

      // Reset and close form
      productDetailForm.reset();
      productDetailInterface.classList.remove('open');
      diamondOptions.forEach(opt => opt.classList.remove('active'));
      selectedOption = null;
    });
  }

  document.getElementById('product-detail-cancel').addEventListener('click', () => {
    // Reset form
    productDetailForm.reset();
    // Remove active class from all options
    diamondOptions.forEach(opt => opt.classList.remove('active'));
    selectedOption = null;
    // Close interface
    productDetailInterface.classList.remove('open');
  });

  document.getElementById('product-detail-close').addEventListener('click', () => {
    // Reset form
    productDetailForm.reset();
    // Remove active class from all options
    diamondOptions.forEach(opt => opt.classList.remove('active'));
    selectedOption = null;
    // Close interface
    productDetailInterface.classList.remove('open');
  });

  // PUBG Modal Handling
  const pubgCard = document.querySelector('.product-card:nth-child(2)');
  const pubgDetailInterface = document.getElementById('pubg-detail-interface');
  const pubgDetailClose = document.getElementById('pubg-detail-close');
  const pubgDetailForm = document.getElementById('pubg-detail-form');
  
  if (pubgCard) {
    pubgCard.addEventListener('click', () => {
      pubgDetailInterface.classList.add('open');
    });
  }

  if (pubgDetailClose) {
    pubgDetailClose.addEventListener('click', () => {
      resetPubgForm();
      pubgDetailInterface.classList.remove('open');
    });
  }

  if (pubgDetailInterface) {
    pubgDetailInterface.addEventListener('click', (e) => {
      if (e.target === pubgDetailInterface) {
        resetPubgForm();
        pubgDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle PUBG diamond options
  const pubgDiamondOptions = pubgDetailInterface ? pubgDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedPubgOption = null;

  pubgDiamondOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      pubgDiamondOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedPubgOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset PUBG form
  const resetPubgForm = () => {
    if (pubgDetailForm) {
      pubgDetailForm.reset();
    }
    pubgDiamondOptions.forEach(opt => opt.classList.remove('active'));
    selectedPubgOption = null;
  };

  if (pubgDetailForm) {
    pubgDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedPubgOption) {
        alert('Please select a UC package');
        return;
      }

      const playerId = document.getElementById('pubg-player-id').value;
      if (!playerId) {
        alert('Please enter your Player ID');
        return;
      }

      // Get price from selected option
      const priceText = selectedPubgOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful!');

      // Reset and close form
      resetPubgForm();
      pubgDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('pubg-detail-cancel').addEventListener('click', () => {
    resetPubgForm();
    pubgDetailInterface.classList.remove('open');
  });
  
  // CODM Modal Handling
  const codmCard = document.querySelector('.product-card:nth-child(3)');
  const codmDetailInterface = document.getElementById('codm-detail-interface');
  const codmDetailClose = document.getElementById('codm-detail-close');
  const codmDetailForm = document.getElementById('codm-detail-form');

  if (codmCard) {
    codmCard.addEventListener('click', () => {
      codmDetailInterface.classList.add('open');
    });
  }

  if (codmDetailClose) {
    codmDetailClose.addEventListener('click', () => {
      resetCodmForm();
      codmDetailInterface.classList.remove('open');
    });
  }

  if (codmDetailInterface) {
    codmDetailInterface.addEventListener('click', (e) => {
      if (e.target === codmDetailInterface) {
        resetCodmForm();
        codmDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle CODM diamond options
  const codmDiamondOptions = codmDetailInterface ? codmDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedCodmOption = null;

  codmDiamondOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      codmDiamondOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedCodmOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset CODM form
  const resetCodmForm = () => {
    if (codmDetailForm) {
      codmDetailForm.reset();
    }
    codmDiamondOptions.forEach(opt => opt.classList.remove('active'));
    selectedCodmOption = null;
  };

  if (codmDetailForm) {
    codmDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedCodmOption) {
        alert('Please select a CP package');
        return;
      }

      const playerId = document.getElementById('codm-player-id').value;
      if (!playerId) {
        alert('Please enter your Player ID');
        return;
      }

      // Get price from selected option
      const priceText = selectedCodmOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful!');

      // Reset and close form
      resetCodmForm();
      codmDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('codm-detail-cancel').addEventListener('click', () => {
    resetCodmForm();
    codmDetailInterface.classList.remove('open');
  });

  const fortniteCard = document.querySelector('.product-card:nth-child(4)');
  const fortniteDetailInterface = document.getElementById('fortnite-detail-interface');
  const fortniteDetailClose = document.getElementById('fortnite-detail-close');
  const fortniteDetailForm = document.getElementById('fortnite-detail-form');

  if (fortniteCard) {
    fortniteCard.addEventListener('click', () => {
      fortniteDetailInterface.classList.add('open');
    });
  }

  if (fortniteDetailClose) {
    fortniteDetailClose.addEventListener('click', () => {
      resetFortniteForm();
      fortniteDetailInterface.classList.remove('open');
    });
  }

  if (fortniteDetailInterface) {
    fortniteDetailInterface.addEventListener('click', (e) => {
      if (e.target === fortniteDetailInterface) {
        resetFortniteForm();
        fortniteDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle Fortnite V-Bucks options
  const fortniteVBuckOptions = fortniteDetailInterface ? fortniteDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedFortniteOption = null;

  fortniteVBuckOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      fortniteVBuckOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedFortniteOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset Fortnite form
  const resetFortniteForm = () => {
    if (fortniteDetailForm) {
      fortniteDetailForm.reset();
    }
    fortniteVBuckOptions.forEach(opt => opt.classList.remove('active'));
    selectedFortniteOption = null;
  };

  if (fortniteDetailForm) {
    fortniteDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedFortniteOption) {
        alert('Please select a V-Bucks package');
        return;
      }

      const playerId = document.getElementById('fortnite-player-id').value;
      if (!playerId) {
        alert('Please enter your Player ID');
        return;
      }

      // Get price from selected option
      const priceText = selectedFortniteOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful!');

      // Reset and close form
      resetFortniteForm();
      fortniteDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('fortnite-detail-cancel').addEventListener('click', () => {
    resetFortniteForm();
    fortniteDetailInterface.classList.remove('open');
  });

  // Apple Gift Card Modal Handling
  const appleCard = document.querySelector('.product-card:nth-child(5)');
  const appleDetailInterface = document.getElementById('apple-detail-interface');
  const appleDetailClose = document.getElementById('apple-detail-close');
  const appleDetailForm = document.getElementById('apple-detail-form');

  if (appleCard) {
    appleCard.addEventListener('click', () => {
      appleDetailInterface.classList.add('open');
    });
  }

  if (appleDetailClose) {
    appleDetailClose.addEventListener('click', () => {
      resetAppleForm();
      appleDetailInterface.classList.remove('open');
    });
  }

  if (appleDetailInterface) {
    appleDetailInterface.addEventListener('click', (e) => {
      if (e.target === appleDetailInterface) {
        resetAppleForm();
        appleDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle Apple gift card options
  const appleVoucherOptions = appleDetailInterface ? appleDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedAppleOption = null;

  appleVoucherOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      appleVoucherOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedAppleOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset Apple form
  const resetAppleForm = () => {
    if (appleDetailForm) {
      appleDetailForm.reset();
    }
    appleVoucherOptions.forEach(opt => opt.classList.remove('active'));
    selectedAppleOption = null;
  };

  if (appleDetailForm) {
    appleDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedAppleOption) {
        alert('Please select a voucher amount');
        return;
      }

      const email = document.getElementById('apple-email').value;
      if (!email) {
        alert('Please enter your email address');
        return;
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
      }

      // Get price from selected option
      const priceText = selectedAppleOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful! Voucher has been sent to your email.');

      // Reset and close form
      resetAppleForm();
      appleDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('apple-detail-cancel').addEventListener('click', () => {
    resetAppleForm();
    appleDetailInterface.classList.remove('open');
  });

  // Google Play Gift Card Modal Handling
  const googleCard = document.querySelector('.product-card:nth-child(6)');
  const googleDetailInterface = document.getElementById('google-detail-interface');
  const googleDetailClose = document.getElementById('google-detail-close');
  const googleDetailForm = document.getElementById('google-detail-form');

  if (googleCard) {
    googleCard.addEventListener('click', () => {
      googleDetailInterface.classList.add('open');
    });
  }

  if (googleDetailClose) {
    googleDetailClose.addEventListener('click', () => {
      resetGoogleForm();
      googleDetailInterface.classList.remove('open');
    });
  }

  if (googleDetailInterface) {
    googleDetailInterface.addEventListener('click', (e) => {
      if (e.target === googleDetailInterface) {
        resetGoogleForm();
        googleDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle Google Play gift card options
  const googleVoucherOptions = googleDetailInterface ? googleDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedGoogleOption = null;

  googleVoucherOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      googleVoucherOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedGoogleOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset Google Play form
  const resetGoogleForm = () => {
    if (googleDetailForm) {
      googleDetailForm.reset();
    }
    googleVoucherOptions.forEach(opt => opt.classList.remove('active'));
    selectedGoogleOption = null;
  };

  if (googleDetailForm) {
    googleDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedGoogleOption) {
        alert('Please select a voucher amount');
        return;
      }

      const email = document.getElementById('google-email').value;
      if (!email) {
        alert('Please enter your email address');
        return;
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
      }

      // Get price from selected option
      const priceText = selectedGoogleOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful! Voucher has been sent to your email.');

      // Reset and close form
      resetGoogleForm();
      googleDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('google-detail-cancel').addEventListener('click', () => {
    resetGoogleForm();
    googleDetailInterface.classList.remove('open');
  });

  const steamCard = document.querySelector('.product-card:nth-child(7)');
  const steamDetailInterface = document.getElementById('steam-detail-interface');
  const steamDetailClose = document.getElementById('steam-detail-close');
  const steamDetailForm = document.getElementById('steam-detail-form');

  if (steamCard) {
    steamCard.addEventListener('click', () => {
      steamDetailInterface.classList.add('open');
    });
  }

  if (steamDetailClose) {
    steamDetailClose.addEventListener('click', () => {
      resetSteamForm();
      steamDetailInterface.classList.remove('open');
    });
  }

  if (steamDetailInterface) {
    steamDetailInterface.addEventListener('click', (e) => {
      if (e.target === steamDetailInterface) {
        resetSteamForm();
        steamDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle Steam card options
  const steamCardOptions = steamDetailInterface ? steamDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedSteamOption = null;

  steamCardOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      steamCardOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedSteamOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset Steam form
  const resetSteamForm = () => {
    if (steamDetailForm) {
      steamDetailForm.reset();
    }
    steamCardOptions.forEach(opt => opt.classList.remove('active'));
    selectedSteamOption = null;
  };

  if (steamDetailForm) {
    steamDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedSteamOption) {
        alert('Please select a Steam card amount');
        return;
      }

      const email = document.getElementById('steam-email').value;
      if (!email) {
        alert('Please enter your email address');
        return;
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
      }

      // Get price from selected option
      const priceText = selectedSteamOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful! Voucher has been sent to your email.');

      // Reset and close form
      resetSteamForm();
      steamDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('steam-detail-cancel').addEventListener('click', () => {
    resetSteamForm();
    steamDetailInterface.classList.remove('open');
  });

  // Function to add new transaction to history
  const addTransactionToHistory = (transactionData) => {
    const transactionsList = document.querySelector('.transactions-list');
    const currentDate = new Date();
    const timeString = currentDate.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit', 
      hour12: true 
    });

    const transaction = document.createElement('div');
    transaction.className = 'transaction';
  
    const isDebit = transactionData.amount < 0;
    const iconClass = isDebit ? 'withdraw' : 'deposit';
    const iconType = isDebit ? 'fa-arrow-up' : 'fa-arrow-down';
  
    transaction.innerHTML = `
      <div class="transaction-icon ${iconClass}">
        <i class="fas ${iconType}"></i>
      </div>
      <div class="transaction-details">
        <span class="transaction-title">${transactionData.title}</span>
        <span class="transaction-date">Today, ${timeString}</span>
      </div>
      <span class="transaction-amount ${iconClass}">${isDebit ? '-' : '+'}${formatCurrency(Math.abs(transactionData.amount))}</span>
    `;

    // Insert new transaction at the top of the list
    if (transactionsList && transactionsList.firstChild) {
      transactionsList.insertBefore(transaction, transactionsList.firstChild);
    } else if (transactionsList) {
      transactionsList.appendChild(transaction);
    }

    // Add fade-in animation
    transaction.style.opacity = '0';
    transaction.style.transform = 'translateY(-10px)';
    requestAnimationFrame(() => {
      transaction.style.transition = 'all 0.3s ease-out';
      transaction.style.opacity = '1';
      transaction.style.transform = 'translateY(0)';
    });
  };

  // Modify purchase handling in product detail forms to add transactions
  const handlePurchase = async (productName, amount) => {
    if (amount > userState.balance) {
      alert('Insufficient balance for this purchase');
      return false;
    }

    showLoader();
    await new Promise(resolve => setTimeout(resolve, 1500));
  
    userState.balance -= amount;
    updateBalanceDisplay();
  
    // Add transaction to history
    addTransactionToHistory({
      title: `Purchase: ${productName}`,
      amount: -amount
    });
  
    hideLoader();
    alert('Purchase successful!');
    return true;
  };

  // Update all product form submissions to use the new handlePurchase function
  document.querySelectorAll('[id$=detail-form]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formId = form.id;
      const productType = formId.replace('-detail-form', '');
      let selectedOption = null;
      
      // Get the selected option based on the form
      switch(productType) {
        case 'product':
          selectedOption = selectedOption;
          break;
        case 'pubg':
          selectedOption = selectedPubgOption;
          break;
        case 'codm':
          selectedOption = selectedCodmOption;
        // ... add cases for other products
      }
      
      if (!selectedOption) {
        alert('Please select a package');
        return;
      }
      
      const priceText = selectedOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));
      const productName = form.closest('.product-detail-content').querySelector('h2').textContent;
      
      const success = await handlePurchase(productName, price);
      if (success) {
        form.reset();
        form.closest('.product-detail-interface').classList.remove('open');
      }
    });
  });

  const stocksBtn = document.querySelector('.secondary-btn:first-child');
  const stocksInterface = document.getElementById('stocks-interface');
  const stocksClose = stocksInterface ? document.getElementById('stocks-close') : null;

  if (stocksInterface && stocksClose) {
    stocksClose.addEventListener('click', () => {
      stocksInterface.classList.remove('open');
    });
  }

  // Only add Buy/Sell button handlers if elements exist
  const buyButtons = document.querySelectorAll('.buy-btn, .sell-btn');
  if (buyButtons.length > 0) {
    buyButtons.forEach(btn => {
      btn.addEventListener('click', async function() {
        const action = this.classList.contains('buy-btn') ? 'Buy' : 'Sell';
        const stockCard = this.closest('.stock-card');
        if (!stockCard) return;
        
        const stockName = stockCard.querySelector('h3')?.textContent || 'Unknown Stock';
        alert(`${action} order for ${stockName} will be available soon!`);

        // Add haptic feedback if available
        if (window.navigator.vibrate) {
          window.navigator.vibrate(50);
        }
      });
    });
  }

  // Add safety checks for feature cards
  if (featureCards.length > 0) {
    featureCards.forEach(card => {
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px)';
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
      });
    });
  }

  // Add safety checks for tasks interface
  const tasksInterface = document.getElementById('tasks-interface');
  const tasksClose = tasksInterface ? document.getElementById('tasks-close') : null;
  const warningModal = document.getElementById('warning-modal');
  const warningClose = warningModal ? warningModal.querySelector('.warning-close') : null;

  if (tasksClose) {
    tasksClose.addEventListener('click', () => {
      tasksInterface.classList.remove('open');
    });
  }

  if (warningClose && warningModal) {
    warningClose.addEventListener('click', () => {
      warningModal.classList.remove('open');
    });
  }

  // Add safety check for claim buttons
  const claimButtons = document.querySelectorAll('.claim-btn');
  if (claimButtons.length > 0) {
    const claimedTasks = new Set();

    claimButtons.forEach(btn => {
      btn.addEventListener('click', async function() {
        const platform = this.getAttribute('data-platform');
        if (!platform) return;
        
        if (claimedTasks.has(platform)) {
          alert('You have already claimed this reward!');
          return;
        }

        const isVerified = await verifyTask(platform);
        
        if (isVerified) {
          userState.balance += 0.20;
          updateBalanceDisplay();
          
          this.classList.add('claimed');
          this.innerHTML = '<i class="fas fa-check"></i> Claimed';
          this.disabled = true;
          claimedTasks.add(platform);
          
          addTransactionToHistory({
            title: `Task Reward: ${platform}`,
            amount: 0.20
          });
          
          alert('Reward claimed successfully!');
        } else if (warningModal) {
          warningModal.classList.add('open');
        }
      });
    });
  }

  async function verifyTask(platform) {
    const random = Math.random();
    await new Promise(resolve => setTimeout(resolve, 1500));
    return random > 0.3;
  }

  // PlayStation Modal Handling
  const playstationCard = document.querySelector('.product-card:nth-child(8)'); // Get the PlayStation card
  const playstationDetailInterface = document.getElementById('playstation-detail-interface');
  const playstationDetailClose = document.getElementById('playstation-detail-close');
  const playstationDetailForm = document.getElementById('playstation-detail-form');

  if (playstationCard) {
    playstationCard.addEventListener('click', () => {
      playstationDetailInterface.classList.add('open');
    });
  }

  if (playstationDetailClose) {
    playstationDetailClose.addEventListener('click', () => {
      resetPlaystationForm();
      playstationDetailInterface.classList.remove('open');
    });
  }

  if (playstationDetailInterface) {
    playstationDetailInterface.addEventListener('click', (e) => {
      if (e.target === playstationDetailInterface) {
        resetPlaystationForm();
        playstationDetailInterface.classList.remove('open');
      }
    });
  }

  // Handle PlayStation card options
  const playstationVoucherOptions = playstationDetailInterface ? playstationDetailInterface.querySelectorAll('.diamond-option') : [];
  let selectedPlaystationOption = null;

  playstationVoucherOptions.forEach(option => {
    option.addEventListener('click', () => {
      // Remove active class from all options
      playstationVoucherOptions.forEach(opt => opt.classList.remove('active'));
      // Add active class to selected option
      option.classList.add('active');
      selectedPlaystationOption = option;

      // Add haptic feedback if available
      if (window.navigator.vibrate) {
        window.navigator.vibrate(50);
      }
    });
  });

  // Function to reset PlayStation form
  const resetPlaystationForm = () => {
    if (playstationDetailForm) {
      playstationDetailForm.reset();
    }
    playstationVoucherOptions.forEach(opt => opt.classList.remove('active'));
    selectedPlaystationOption = null;
  };

  if (playstationDetailForm) {
    playstationDetailForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!selectedPlaystationOption) {
        alert('Please select a PSN card amount');
        return;
      }

      const email = document.getElementById('playstation-email').value;
      if (!email) {
        alert('Please enter your email address');
        return;
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
      }

      // Get price from selected option
      const priceText = selectedPlaystationOption.querySelector('.diamond-price').textContent;
      const price = parseFloat(priceText.replace('$', ''));

      // Check if user has sufficient balance
      if (price > userState.balance) {
        alert('Insufficient balance for this purchase');
        return;
      }

      // Show loader
      showLoader();

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Deduct amount from balance
      userState.balance -= price;
      updateBalanceDisplay();

      // Add transaction to history
      addTransactionToHistory({
        title: 'Purchase: PlayStation Gift Card',
        amount: -price
      });

      // Hide loader
      hideLoader();

      // Show success message
      alert('Purchase successful! PSN card has been sent to your email.');

      // Reset and close form
      resetPlaystationForm();
      playstationDetailInterface.classList.remove('open');
    });
  }

  document.getElementById('playstation-detail-cancel').addEventListener('click', () => {
    resetPlaystationForm();
    playstationDetailInterface.classList.remove('open');
  });

  // Function to show tournament modal
  const showTournamentModal = () => {
    const modal = document.createElement('div');
    modal.className = 'warning-modal open';
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="warning-content">
        <div class="gearbox">
          <div class="overlay"></div>
          <div class="gear one">
            <div class="gear-inner">
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
            </div>
          </div>
          <div class="gear two">
            <div class="gear-inner">
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
            </div>
          </div>
          <div class="gear three">
            <div class="gear-inner">
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
            </div>
          </div>
          <div class="gear four large">
            <div class="gear-inner">
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
              <div class="bar"></div>
            </div>
          </div>
        </div>
        <i class="fas fa-trophy" style="color: #FFD700;"></i>
        <h3>Tournaments Coming Soon!</h3>
        <p>We're working hard to bring you exciting tournaments with amazing prizes. Stay tuned!</p>
        <button class="warning-close">Got it!</button>
      </div>
    `;

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('.warning-close');
    closeBtn.addEventListener('click', () => {
      modal.remove();
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  };

  // Review form handling
  const reviewForm = document.getElementById('review-form');
  const starRating = document.getElementById('star-rating');
  const stars = starRating ? starRating.querySelectorAll('.star') : [];
  let selectedRating = 0;

  // Star rating functionality
  if (stars.length > 0) {
    stars.forEach((star, index) => {
      star.addEventListener('click', () => {
        selectedRating = index + 1;
        updateStarDisplay();
        
        // Add haptic feedback if available
        if (window.navigator.vibrate) {
          window.navigator.vibrate(50);
        }
      });

      star.addEventListener('mouseenter', () => {
        highlightStars(index + 1);
      });
    });

    if (starRating) {
      starRating.addEventListener('mouseleave', () => {
        updateStarDisplay();
      });
    }
  }

  const updateStarDisplay = () => {
    stars.forEach((star, index) => {
      const icon = star.querySelector('i');
      if (index < selectedRating) {
        star.classList.add('active');
        icon.className = 'fas fa-star';
      } else {
        star.classList.remove('active');
        icon.className = 'far fa-star';
      }
    });
  };

  const highlightStars = (rating) => {
    stars.forEach((star, index) => {
      const icon = star.querySelector('i');
      if (index < rating) {
        star.classList.add('active');
        icon.className = 'fas fa-star';
      } else {
        star.classList.remove('active');
        icon.className = 'far fa-star';
      }
    });
  };

  // Review form submission
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (selectedRating === 0) {
        alert('Please select a star rating');
        return;
      }

      const reviewerName = document.getElementById('reviewer-name').value;
      const reviewTitle = document.getElementById('review-title').value;
      const reviewText = document.getElementById('review-text').value;

      if (!reviewerName || !reviewTitle || !reviewText) {
        alert('Please fill in all fields');
        return;
      }

      // Show loader
      showLoader();

      // Simulate submission
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create new review element
      const newReview = createReviewElement({
        name: reviewerName,
        title: reviewTitle,
        content: reviewText,
        rating: selectedRating,
        date: 'Just now',
        avatar: reviewerName.split(' ').map(n => n[0]).join('').toUpperCase()
      });

      // Add to reviews grid
      const reviewsGrid = document.querySelector('.reviews-grid');
      if (reviewsGrid) {
        reviewsGrid.insertBefore(newReview, reviewsGrid.firstChild);
      }

      // Hide loader
      hideLoader();

      // Reset form
      reviewForm.reset();
      selectedRating = 0;
      updateStarDisplay();

      // Show success message
      alert('Thank you for your review! It has been submitted successfully.');

      // Scroll to the new review
      newReview.scrollIntoView({ behavior: 'smooth' });
    });
  }

  // Function to create a new review element
  const createReviewElement = (reviewData) => {
    const reviewCard = document.createElement('div');
    reviewCard.className = 'review-card';
    reviewCard.style.opacity = '0';
    reviewCard.style.transform = 'translateY(20px)';

    const starsHtml = Array.from({ length: 5 }, (_, i) => {
      const starClass = i < reviewData.rating ? 'fas fa-star' : 'far fa-star';
      return `<i class="${starClass}"></i>`;
    }).join('');

    reviewCard.innerHTML = `
      <div class="review-header">
        <div class="reviewer-info">
          <div class="reviewer-avatar">${reviewData.avatar}</div>
          <div class="reviewer-details">
            <h4>${reviewData.name}</h4>
            <span class="review-date">${reviewData.date}</span>
          </div>
        </div>
        <div class="review-rating">
          ${starsHtml}
        </div>
      </div>
      <div class="review-content">
        <h5>${reviewData.title}</h5>
        <p>${reviewData.content}</p>
      </div>
      <div class="review-verified">
        <i class="fas fa-check-circle"></i>
        <span>Verified purchase</span>
      </div>
    `;

    // Animate in
    setTimeout(() => {
      reviewCard.style.transition = 'all 0.5s ease';
      reviewCard.style.opacity = '1';
      reviewCard.style.transform = 'translateY(0)';
    }, 100);

    return reviewCard;
  };
});