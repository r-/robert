const RobotApi = (() => {
    /**
     * Sends motor speed commands to the robot server.
     * @param {number} left - Speed for the left motor.
     * @param {number} right - Speed for the right motor.
     */
    const sendMotorCommand = (left, right) => {
        console.log("Sending motor speeds:", left, right);

        const data = JSON.stringify({ left, right });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `motors/control_motor`, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("Motor command response:", JSON.parse(xhr.responseText));
                } else {
                    console.error(`Motor API error: ${xhr.status} - ${xhr.statusText}`);
                }
            }
        };

        xhr.send(data);
    };

    /**
     * Sends camera movement commands to the robot server.
     * @param {number} up - Camera movement speed.
     */
    const sendCameraCommand = (up) => {
        console.log("Sending camera speeds:", up);

        const data = JSON.stringify({ up });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `motors/control_camera`, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("Camera command response:", JSON.parse(xhr.responseText));
                } else {
                    console.error(`Camera API error: ${xhr.status} - ${xhr.statusText}`);
                }
            }
        };

        xhr.send(data);
    };

    /**
     * Sends a shoot command to the robot server.
     */
    const shoot = () => {
        console.log("Sending shoot command...");

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/shoot/shoot", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("Shoot response:", JSON.parse(xhr.responseText));
                    Terminal.logToTerminal(JSON.stringify(JSON.parse(xhr.responseText)).replace(/"/g, ''), true);
                } else {
                    console.error(`Shoot API error: ${xhr.status} - ${xhr.statusText}`);
                    Terminal.logToTerminal(JSON.stringify(JSON.parse(xhr.responseText))
                    .replace(/{/g, '')
                    .replace(/}/g, '')
                    .replace(/"/g, ''),
                    true);
                }
            }
        };

        xhr.send();
    };

    /**
     * Sends a request to join the server with a player ID.
     * @param {string} playerId - Unique identifier for the player.
     */
    const joinServer = (playerId) => {
        console.log("Joining server with player ID:", playerId);

        const data = JSON.stringify({ player_id: playerId });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/network/join_server", true);  // Adjusted to match your Flask route
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("Join server response:", JSON.parse(xhr.responseText));
                } else {
                    console.error(`Join server error: ${xhr.status} - ${xhr.statusText}`);
                }
            }
        };

        xhr.send(data);
    };

    return { sendMotorCommand, sendCameraCommand, shoot, joinServer };
})();
