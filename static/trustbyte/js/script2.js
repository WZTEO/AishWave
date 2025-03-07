document.addEventListener("DOMContentLoaded", function () {
    const paymentOptionsContainer = document.querySelector(".payment-options");
    const inputFieldsContainer = document.getElementById("input-fields");
    const proceedBtn = document.getElementById("proceed-btn");
    const cancelBtn = document.getElementById("cancel-btn");

    proceedBtn.disabled = true; // Initially disable proceed

    paymentOptionsContainer.addEventListener("click", function (event) {
        const selectedOption = event.target.closest(".payment-option");
        if (!selectedOption) return;

        document.querySelectorAll(".payment-option").forEach((opt) => opt.classList.remove("selected"));
        selectedOption.classList.add("selected");

        // Insert fields inside the form
        generateFormFields(selectedOption.dataset.provider);

        inputFieldsContainer.classList.add("active");
        proceedBtn.disabled = true;
    });

    cancelBtn.addEventListener("click", resetForm);

    function generateFormFields(provider) {
        const formTemplates = {
            mtn: `
                <div class="form-group">
                    <label for="mtn-phone">MTN Phone Number</label>
                    <input type="tel" name="account_number" id="mtn-phone" required>
                </div>
                <div class="form-group">
                    <label for="mtn-name">Account Name</label>
                    <input type="text" name="account_name" id="mtn-name" required>
                </div>
                <div class="form-group">
                    <label for="mtn-amount">Amount (GHS)</label>
                    <input type="number"  name="amount" id="mtn-amount" required>
                </div>
                <input type="hidden" name="provider" value="mtn">
            `,
            vodafone: `
                <div class="form-group">
                    <label for="vodafone-phone">Vodafone Phone Number</label>
                    <input type="tel" name="account_number" id="vodafone-phone" required>
                </div>
                <div class="form-group">
                    <label for="vodafone-name">Account Name</label>
                    <input type="text" name="account_name" id="vodafone-name" required>
                </div>
                <div class="form-group">
                    <label for="vodafone-amount">Amount (GHS)</label>
                    <input type="number"  name="amount" id="vodafone-amount" required>
                </div>
                <input type="hidden" name="provider" value="vodafone">
            `,
            binance: `
                <div class="form-group">
                    <label for="binance-id">Binance ID</label>
                    <input type="text" name="account_number" id="binance-id" required>
                </div>
                <div class="form-group">
                    <label for="binance-amount">Amount (USD)</label>
                    <input type="number" name="amount" id="binance-amount" required>
                </div>
                <input type="hidden" name="account_name" value="Binance Account">
                <input type="hidden" name="provider" value="binance">
            `,
        };

        // Replace content inside the form
        inputFieldsContainer.innerHTML = formTemplates[provider] || "";

         // Animate form fields appearing in sequence
         document.querySelectorAll('.form-group').forEach((formGroup, index) => {
            setTimeout(() => formGroup.classList.add('visible'), 100 * (index + 1));
        });

        inputFieldsContainer.querySelectorAll("input").forEach((input) => {
            input.addEventListener("input", () => {
                proceedBtn.disabled = !validateForm();
            });
        });
    }

    function validateForm() {
        const inputs = inputFieldsContainer.querySelectorAll("input");
        return Array.from(inputs).every((input) => input.value.trim() !== "");
    }

    function resetForm() {
        document.querySelectorAll(".payment-option").forEach((opt) => opt.classList.remove("selected"));
        inputFieldsContainer.classList.remove("active");
        inputFieldsContainer.innerHTML = "";
        proceedBtn.disabled = true;
    }
});