// manage shadow DOM
function grRoot() {
  const app = document.querySelector('gradio-app');
  return app && app.shadowRoot ? app.shadowRoot : document; // fallback if no shadow DOM
}
function byId(id)     { return grRoot().getElementById(id); }
function qs(sel)      { return grRoot().querySelector(sel); }
function qsa(sel)     { return grRoot().querySelectorAll(sel); }

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
    let suffix = mobile ? "_mobile" : "";
    const input1 = byId('input1'+suffix)?.value || "";
    const input2 = byId('input2'+suffix)?.value || "";
    const input3 = byId('input3'+suffix)?.value || "";

    // Check if all three inputs are valid digits
    const valid = /^[0-9]{1}$/.test(input1) && /^[0-9]{1}$/.test(input2) && /^[0-9]{1}$/.test(input3);

    // Enable or disable the button based on the validity of the inputs
    const button = qs('#check_number_button');
    if (button) button.disabled = !valid;  // Disable if not all inputs are valid

    const button_mobile = qs('#check_number_button_mobile');
    if (button_mobile) button_mobile.disabled = !valid;  // Disable if not all inputs are valid
}

// Add digit to the next available input field when a keypad button is clicked
function addDigit(digit) {
  // Find the first empty input field
  let inputs = qsa('.digit-input');
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
  let inputs = qsa('.digit-input-mobile');
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
  let inputs = qsa('.digit-input');

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
  let inputs = qsa('.digit-input-mobile');

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


const observer = new MutationObserver(() => {
  const canvas = byId("finish_chart");
  if (canvas) {
    drawChart();
    observer.disconnect(); // stop after first render
  }
});

observer.observe(grRoot(), { childList: true, subtree: true });

function drawChart() {
    const number_correct_guesses = parseInt(qs('#number_correct_guesses_textbox textarea')?.value);
    const number_wrong_guesses = parseInt(qs('#number_wrong_guesses_textbox textarea')?.value);

    const ctx = byId('finish_chart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Richtig geraten', 'Falsch geraten'],
            datasets: [{
                label: 'Bisherige Antworten',
                data: [number_correct_guesses, number_wrong_guesses], // replace with real values
                backgroundColor: ['green', 'red'],
                barThickness: 40 // smaller number = thinner bars

            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Bisherige Antworten'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            }
        }
    });
}


function getNumberGuess() {
    input1 = byId('input1').value;
    input2 = byId('input2').value;
    input3 = byId('input3').value;
    return input1 + input2 + input3;
}

function getNumberGuessMobile() {
    input1 = byId('input1_mobile').value;
    input2 = byId('input2_mobile').value;
    input3 = byId('input3_mobile').value;
    return input1 + input2 + input3;
}



document.addEventListener('DOMContentLoaded', function () {
    const observer = new MutationObserver(() => {
        const val = qs('textarea[aria-label="textbox"]').value;
        console.log("Updated value:", val);
    });

    observer.observe(document.body, { childList: true, subtree: true });
});

