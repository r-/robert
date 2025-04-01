// Update displayed values as sliders are adjusted
document.getElementById('framerate-slider').addEventListener('input', function () {
    document.getElementById('framerate-value').textContent = this.value + " FPS";
});

document.getElementById('quality-slider').addEventListener('input', function () {
    document.getElementById('quality-value').textContent = this.value;
});

document.getElementById('motor-speed-slider').addEventListener('input', function () {
    document.getElementById('motor-speed-value').textContent = this.value;
});

// Apply the new configuration to the backend
document.getElementById('apply-config').addEventListener('click', function () {
    const framerate = document.getElementById('framerate-slider').value;
    const quality = document.getElementById('quality-slider').value;
    const motorSpeed = document.getElementById('motor-speed-slider').value;

    fetch('config/set_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            framerate: framerate,
            quality: quality,
            motor_speed: motorSpeed
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Configuration updated:', data);
            location.reload();
        })
        .catch(err => {
            console.error('Error updating configuration:', err);
            alert('Failed to update configuration.');
        });
});

// Fetch current configuration on page load
window.addEventListener('DOMContentLoaded', () => {
    fetch('config/get_config')
        .then(response => response.json())
        .then(data => {
            document.getElementById('framerate-slider').value = data.CAMERA_FRAMERATE;
            document.getElementById('quality-slider').value = data.JPEG_QUALITY;
            document.getElementById('motor-speed-slider').value = data.MOTOR_SPEED;

            document.getElementById('framerate-value').textContent = data.CAMERA_FRAMERATE + " FPS";
            document.getElementById('quality-value').textContent = data.JPEG_QUALITY;
            document.getElementById('motor-speed-value').textContent = data.MOTOR_SPEED;
        })
        .catch(err => {
            console.error('Error fetching current config:', err);
        });
});