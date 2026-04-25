document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const spinner = document.getElementById('spinner');
    const resultBox = document.getElementById('result');
    const resultTitle = resultBox.querySelector('.result-title');
    const resultProb = resultBox.querySelector('.result-prob');

    // Reset UI
    resultBox.style.display = 'none';
    spinner.style.display = 'block';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Update result box
        resultTitle.textContent = `Verdict: ${result.verdict}`;
        resultProb.textContent = `Probability of being fake: ${(result.final_probability * 100).toFixed(2)}%`;
        
        if (result.verdict === 'Fake') {
            resultBox.className = 'result-box fake';
        } else {
            resultBox.className = 'result-box real';
        }

    } catch (error) {
        console.error('Prediction error:', error);
        resultTitle.textContent = 'Error';
        resultProb.textContent = 'An error occurred during analysis.';
        resultBox.className = 'result-box fake'; // Show error in red
    } finally {
        spinner.style.display = 'none';
        resultBox.style.display = 'block';
    }
});
