// Javascript for Curated
// Handles color search logic, favorite button interaction, and zoom in/out functionality on images


// Favorite button Handle click logic:

document.addEventListener('DOMContentLoaded', function () {
    // Add click event listeners to all favorite buttons
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            const artworkId = button.dataset.artworkId; // Get the artwork ID from the button's data attribute
            const isLiked = button.dataset.liked === 'true'; // Determine if the artwork is already liked

            // Send a POST request to toggle the favorite status
            fetch(`/artwork/${artworkId}/favorite`, { method: 'POST' })
                .then(response => response.json()) // Parse the JSON response
                .then(data => {
                    button.dataset.liked = data.liked; // Update the button's data-liked attribute
                    const icon = button.querySelector('i'); // Get the icon element within the button

                    // Toggle the icon's class based on the favorite status
                    if (data.liked) {
                        icon.classList.remove('fa-regular');
                        icon.classList.add('fa-solid');
                    } else {
                        icon.classList.remove('fa-solid');
                        icon.classList.add('fa-regular');
                    }
                })
                .catch(error => console.error('Error:', error)); // Log any errors to the console
        });
    });
});


// Color picker logic:
document.getElementById('color-picker').addEventListener('input', function () {
    const hexColor = this.value; // Get the selected hex color value
    const hslColor = hexToHsl(hexColor); // Convert the hex color to HSL
    document.getElementById('color-form').elements['color'].value = JSON.stringify(hslColor); // Store the HSL value in the hidden form field
    console.log('Selected Color:', hslColor); // Log the selected color
});

// Convert hex color from color picker to HSL values to match API values
function hexToHsl(hex) {
    let r = 0, g = 0, b = 0;

    // Convert hex color to RGB values
    if (hex.length === 4) {
        r = parseInt(hex[1] + hex[1], 16);
        g = parseInt(hex[2] + hex[2], 16);
        b = parseInt(hex[3] + hex[3], 16);
    } else if (hex.length === 7) {
        r = parseInt(hex[1] + hex[2], 16);
        g = parseInt(hex[3] + hex[4], 16);
        b = parseInt(hex[5] + hex[6], 16);
    }

    r /= 255;
    g /= 255;
    b /= 255;

    // Calculate lightness and saturation
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;  // Achromatic (no hue)
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

        // Calculate hue based on the max RGB component
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }

    return {
        h: Math.round(h * 360),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

// Handle color form submission: 

document.getElementById('color-form').addEventListener('submit', function (event) {
    const colorValue = document.getElementById('color-form').elements['color'].value;
    console.log('Submitting Color Value:', colorValue);

    // Prevent form submission if no color is selected
    if (!colorValue) {
        event.preventDefault(); // Stop the form from submitting
        alert('Please select a color.'); // Alert the user
    }
});

// Zoom in features for fullscreen image viewing
function openFullscreen() {
    // Show the fullscreen overlay
    document.getElementById('fullscreen-overlay').classList.add('show');
}

function closeFullscreen() {
    // Hide the fullscreen overlay
    document.getElementById('fullscreen-overlay').classList.remove('show');
}

function zoomIn() {
    // Apply zoom-in effect to the image
    const img = document.getElementById('fullscreen-image');
    img.classList.add('zoomed-in');
    img.classList.remove('zoomed-out');
}

function zoomOut() {
    // Apply zoom-out effect to the image
    const img = document.getElementById('fullscreen-image');
    img.classList.remove('zoomed-in');
    img.classList.add('zoomed-out');
}
