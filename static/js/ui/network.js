function updateNetworkSpeed() {
    fetch('network/network_speed')
        .then(response => response.json())
        .then(data => {
            document.getElementById('upload-speed').textContent = data.upload_mbps + " Mbps";
            document.getElementById('download-speed').textContent = data.download_mbps + " Mbps";
        })
        .catch(err => console.error('Error fetching network speed:', err));
}

// Refresh speed every 2 seconds
setInterval(updateNetworkSpeed, 2000);

// Initial load
updateNetworkSpeed();