const Infobox = (() => {

    const updateHpBar = () => {
        console.log("updateHpBar called")
        // Send a POST request to the Flask server
        data = GameServerApi.sendCommand(`/hp`)
        .then(data => {
            console.log("updateHpBar recieved information")
            if (data.status === "success") {
                // Get the player's current health from the response
                const health = data.player.health;
    
                // Update the HP bar
                const hpBar = document.getElementById('hp-bar');
                const hpPercentage = (health / 10) * 100; // Assuming max health is 10
                hpBar.style.width = hpPercentage + "%";
    
                // Optionally, update text or other indicators
                const hpText = document.getElementById('hp-text');
                hpText.textContent = `HP: ${health}/10`;
            } else {
                console.error("Error fetching HP:", data.message);
            }
        })
        .catch(error => {
            console.error("Failed to fetch HP:", error);
        });
    }
    
    // Call the update function periodically, e.g., every second
    const startHpBar = () => {
        console.log("startHpBar called")
        setInterval(updateHpBar, 1000);
    }
    
    return {startHpBar};

})();