function moveFocus(currentInput, event) {
    // Allow only digits
    currentInput.value = currentInput.value.replace(/[^0-9]/, '');

    // Move focus to the next input if the current one is filled
    if (currentInput.value.length === 1) {
        let nextInput = currentInput.nextElementSibling;
        if (nextInput && nextInput.classList.contains('digit-input')) {
            nextInput.focus();
        }
    }

    // Move focus to the previous input if the user deletes the value
    if (currentInput.value.length === 0) {
        let previousInput = currentInput.previousElementSibling;
        if (previousInput && previousInput.classList.contains('digit-input')) {
            previousInput.focus();
        }
    }

    check_number_guess_valid()
}

function moveFocusMobile(currentInput, event) {
    // Allow only digits
    currentInput.value = currentInput.value.replace(/[^0-9]/, '');

    // Move focus to the next input if the current one is filled
    if (currentInput.value.length === 1) {
        let nextInput = currentInput.nextElementSibling;
        if (nextInput && nextInput.classList.contains('digit-input-mobile')) {
            nextInput.focus();
        }
    }

    // Move focus to the previous input if the user deletes the value
    if (currentInput.value.length === 0) {
        let previousInput = currentInput.previousElementSibling;
        if (previousInput && previousInput.classList.contains('digit-input-mobile')) {
            previousInput.focus();
        }
    }

    check_number_guess_valid(true)
}

function check_number_guess_valid(mobile=false) {
    let suffix = "";
    if (mobile) suffix = "_mobile"
    const input1 = document.getElementById('input1'+suffix).value;
    const input2 = document.getElementById('input2'+suffix).value;
    const input3 = document.getElementById('input3'+suffix).value;

    // Check if all three inputs are valid digits
    const valid = /^[0-9]{1}$/.test(input1) && /^[0-9]{1}$/.test(input2) && /^[0-9]{1}$/.test(input3);

    // Enable or disable the button based on the validity of the inputs
    const button = document.querySelector('#check_number_button');
    button.disabled = !valid;  // Disable if not all inputs are valid

    const button_mobile = document.querySelector('#check_number_button_mobile');
    button_mobile.disabled = !valid;  // Disable if not all inputs are valid
}

// Add digit to the next available input field when a keypad button is clicked
function addDigit(digit) {
  // Find the first empty input field
  let inputs = document.querySelectorAll('.digit-input');
  for (let input of inputs) {
    if (input.value === '') {
      input.value = digit;  // Set the value of the input to the clicked digit
      input.focus();        // Focus the input field
      break;  // Exit loop after filling the first empty input
    }
  }

  check_number_guess_valid()
}

// Add digit to the next available input field when a keypad button is clicked
function addDigitMobile(digit) {
  // Find the first empty input field
  let inputs = document.querySelectorAll('.digit-input-mobile');
  for (let input of inputs) {
    if (input.value === '') {
      input.value = digit;  // Set the value of the input to the clicked digit
      input.focus();        // Focus the input field
      break;  // Exit loop after filling the first empty input
    }
  }

  check_number_guess_valid(true)
}


// Function to delete the last entered digit
function deleteLastDigit() {
  let inputs = document.querySelectorAll('.digit-input');

  // Loop through inputs in reverse order to find the last non-empty input
  for (let i = inputs.length - 1; i >= 0; i--) {
    if (inputs[i].value !== '') {
      inputs[i].value = '';  // Clear the value of the last filled input
      inputs[i].focus();     // Optionally, focus the cleared input
      break;  // Exit loop after clearing the last digit
    }
  }

  check_number_guess_valid()
}

// Function to delete the last entered digit
function deleteLastDigitMobile() {
  let inputs = document.querySelectorAll('.digit-input-mobile');

  // Loop through inputs in reverse order to find the last non-empty input
  for (let i = inputs.length - 1; i >= 0; i--) {
    if (inputs[i].value !== '') {
      inputs[i].value = '';  // Clear the value of the last filled input
      inputs[i].focus();     // Optionally, focus the cleared input
      break;  // Exit loop after clearing the last digit
    }
  }

  check_number_guess_valid(true)
}


function getNumberGuess() {
    input1 = document.getElementById('input1').value;
    input2 = document.getElementById('input2').value;
    input3 = document.getElementById('input3').value;
    return input1 + input2 + input3;
}

function getNumberGuessMobile() {
    input1 = document.getElementById('input1_mobile').value;
    input2 = document.getElementById('input2_mobile').value;
    input3 = document.getElementById('input3_mobile').value;
    return input1 + input2 + input3;
}