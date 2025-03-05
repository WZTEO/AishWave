document.addEventListener('DOMContentLoaded', () => {
    const countdownEl = document.getElementById('countdown');
    const resendBtn = document.getElementById('resend-btn');
    let countdownValue = 60;
    
    const countdown = setInterval(() => {
        countdownValue--;
        countdownEl.textContent = countdownValue;
        
        if (countdownValue <= 0) {
            clearInterval(countdown);
            resendBtn.disabled = false;
            document.querySelector('.timer').style.display = 'none';
        }
    }, 1000);
    

});