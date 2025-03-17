const RobotApi = (() => {
    /**
     * Sends motor speed commands to the robot server.
     * @param {Object} motorSpeeds - An object containing motor speeds for "left" and "right".
     */
    const sendMotorCommand = (left, right) => {
        console.log("Sending motor speeds:", left, right);
    
        const data = JSON.stringify({ left, right });
    
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/control_motor`, true);  // RELATIVE URL - no CORS issues
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


    activateDelay = 500 // Delay (in ms) before activate command can be used again
    cooldown = false // Assume the activate isn't on delay
    target_id = null

    const activate = () => {
        if (cooldown){
            return
        }
        cooldown = true

        document.querySelector('.video-container').style.border = "5px solid #b30000";

        console.log("Activated")
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `http://${server_ip}:5000/activate`, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("Activate status:", JSON.parse(xhr.responseText));
                    target_id = JSON.parse(xhr.responseText).target_id
                    console.log("in place id", target_id)
                    GameServerApi.sendCommand(`/activate ${target_id}`)
                } else {
                    console.error(`Activate error: ${xhr.status} - ${xhr.statusText}`);
                }
            }
        };

        xhr.send();

        setTimeout(() => {
            cooldown = false
            document.querySelector('.video-container').style.border = "5px solid #ddd"
        }, activateDelay)
    }

    return { sendMotorCommand, activate };
})();