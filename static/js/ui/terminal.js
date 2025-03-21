const Terminal = (() => {
    let serverIp = ""; // Dynamically set server IP

    const logToTerminal = (message) => {
        const terminal = document.getElementById("terminal");
        terminal.innerHTML += `<div>${message}</div>`;
        terminal.scrollTop = terminal.scrollHeight;
    };

    const parseCommand = (input) => {
        const parts = input.split(" ");
        const command = parts[0];

        if (command === "/login" && parts.length === 3) {
            serverIp = parts[1];
            GameServerApi.setServerIp(serverIp);
            GameServerApi.connect(parts[2])
                .then((response) => logToTerminal(response.message)) // Log the greeting message
                .catch((error) => logToTerminal(`Error: ${error.message}`));
            logToTerminal(`Connecting to server at ${serverIp}...`);
            Infobox.startHpBar()
        } else if (serverIp) {
            GameServerApi.sendCommand(input)
                .then((response) => logToTerminal(response.message))
                .catch((error) => logToTerminal(`Error: ${error.message}`));
        } else if (command === "/say") {
            const message = parts.slice(1).join(" "); // Join the rest of the message after "/say"

            // Send the message to the backend using fetch
            fetch("/say", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            })
                .then((response) => response.json())
                .then((data) => logToTerminal(`Speech response: ${data.message}`))
                .catch((error) => logToTerminal(`Error: ${error.message}`));
        }
        else {
            logToTerminal("Please log in first using /login <server_ip> <player_id>.");
        }
    };

    const bindTerminalEvents = () => {
        // Send command on Enter key press
        document.getElementById("command-input").addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                const input = document.getElementById("command-input").value.trim();
                document.getElementById("command-input").value = ""; // Clear input field
                parseCommand(input);
            }
        });

        // Send command on button click
        document.getElementById("send-command").addEventListener("click", () => {
            const input = document.getElementById("command-input").value.trim();
            document.getElementById("command-input").value = ""; // Clear input field
            parseCommand(input);
        });
    };

    return { logToTerminal, bindTerminalEvents };
})();
