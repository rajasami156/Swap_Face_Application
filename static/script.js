// script.js

document.addEventListener('DOMContentLoaded', () => {
    const sourceImageInput = document.getElementById('sourceImage');
    const targetImageInput = document.getElementById('targetImage');
    const sourcePreview = document.getElementById('sourcePreview');
    const targetPreview = document.getElementById('targetPreview');
    const swapButton = document.getElementById('swapButton');
    const resultSection = document.querySelector('.result-section');
    const resultImage = document.getElementById('resultImage');

    // Function to preview images
    function previewImage(input, preview) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
            reader.readAsDataURL(input.files[0]);
        } else {
            preview.src = '#';
            preview.style.display = 'none';
        }
    }

    // Event listeners for image previews
    sourceImageInput.addEventListener('change', () => {
        previewImage(sourceImageInput, sourcePreview);
    });

    targetImageInput.addEventListener('change', () => {
        previewImage(targetImageInput, targetPreview);
    });

    // Event listener for swap button
    swapButton.addEventListener('click', async () => {
        const sourceFile = sourceImageInput.files[0];
        const targetFile = targetImageInput.files[0];

        if (!sourceFile || !targetFile) {
            alert('Please upload both source and target images.');
            return;
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('source_image', sourceFile);
        formData.append('target_image', targetFile);

        // Show loading state
        swapButton.disabled = true;
        swapButton.textContent = 'Swapping...';

        try {
            const response = await fetch('/swap_faces/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                resultImage.src = url;
                resultSection.style.display = 'block';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An unexpected error occurred.');
        } finally {
            // Reset button state
            swapButton.disabled = false;
            swapButton.textContent = 'Swap Faces';
        }
    });
});
