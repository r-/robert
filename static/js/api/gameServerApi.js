const GameServerApi = {
    sendCommand: function(command) {
        return fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command }),
        })
        .then(response => response.json())
        .then(data => data)
        .catch(error => {
            console.error('Error sending command:', error);
            throw new Error('Failed to communicate with the server.');
        });
    }
};

function handleJoinServer() {
    const playerId = prompt("Enter your player ID to join the server:");

    if (playerId) {
        const command = `/login ${server_ip} ${playerId}`;
        
        // Send the join request to the game server API
        GameServerApi.sendCommand(command)
            .then(response => {
                console.log("Join server response:", response);
                Terminal.log(`Server: ${response.message}`);

                if (response.status === "success") {
                    // Successfully joined - redirect to game or update UI
                    onJoinSuccess(playerId);
                }
            })
            .catch(error => {
                console.error("Failed to join server:", error);
                Terminal.log(`Error: ${error.message}`);
            });
    } else {
        console.log("Player ID not entered.");
    }
}

/**
 * Handles post-join actions such as redirecting or updating the UI.
 * @param {string} playerId - The ID of the player who joined.
 */
function onJoinSuccess(playerId) {
    console.log(`Player ${playerId} successfully joined!`);

    // Example: Redirect to game UI
    window.location.href = "/game";  

    // Example: Update UI to show player is connected
    document.getElementById("playerStatus").innerText = `Connected as: ${playerId}`;
}
