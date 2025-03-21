const server_ip = "{{ server_ip }}";

function handleCommand(left, right) {
    console.log(`Sending motor command: ${left}, ${right}`);
    RobotApi.sendMotorCommand(left, right);
}

function handleActivate() {
    console.log("Sending activation request...");
    RobotApi.activate();
}

function handleSendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();

    if (command) {
        console.log(`Sending game server command: ${command}`);
        GameServerApi.sendCommand(command)
            .then(response => {
                console.log("Game server response:", response);
                Terminal.log(`Server: ${response.message}`);
            })
            .catch(error => {
                console.error("Failed to send command:", error);
                Terminal.log(`Error: ${error.message}`);
            });
    } else {
        Terminal.log("Please enter a command.");
    }
}
