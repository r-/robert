function updateNetworkSpeed() {
    fetch('network/network_speed')
        .then(response => response.json())
        .then(data => {
            document.getElementById('upload-speed').textContent = data.upload_mbps + " Mbps";
            document.getElementById('download-speed').textContent = data.download_mbps + " Mbps";
        })
        .catch(err => console.error('Error fetching network speed:', err));
}

setInterval(updateNetworkSpeed, 5000);

// Initial load
updateNetworkSpeed();

setInterval(UpdatePlayerHealth, 2000);
function UpdatePlayerHealth() {
    fetch('network/get_health')  // Make sure the correct route is used
        .then(response => response.json())
        .then(data => {
            let currentHealth = data.currentHealth;
            let maxHealth = data.maxHealth;

            // Check if both currentHealth and maxHealth are valid numbers
            if (isNaN(currentHealth) || isNaN(maxHealth) || maxHealth <= 0) {
                console.error('Invalid health values received:', currentHealth, maxHealth);
                return;
            }

            // Update the text and progress bar
            document.getElementById('hp-text').textContent = `${currentHealth}/${maxHealth}`;

            // Safely calculate progress bar value
            let progressBar = document.getElementById('hp-bar');
            progressBar.value = (currentHealth / maxHealth) * 100;

            const deathScreen = document.getElementById('death-screen');

            // Death screen
            if (currentHealth <= 0) {
                deathScreen.style.display = 'block';
            }
            else
            {
                deathScreen.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching health data:', error);
        });
}

// Call this function to update health when necessary
UpdatePlayerHealth();

