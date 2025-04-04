const Terminal = (() => {
    let serverIp = ""; // Dynamically set server IP

    const logToTerminal = (message) => {
        const terminal = document.getElementById("terminal");
        terminal.innerHTML += `<div>${message}</div>`;
        terminal.scrollTop = terminal.scrollHeight;
    };

    const fetchSystemStatus = () => {
        fetch('motors/get_system_status')
            .then(response => response.json())
            .then(data => {
                // Log each component status
                for (let component in data) {
                    logToTerminal(`${component}: ${data[component]}`);
                }
            })
            .catch(error => {
                logToTerminal(`Error fetching system status: ${error}`);
            });
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

        // Bind button to fetch system status
        document.getElementById("check-system-status").addEventListener("click", () => {
            fetchSystemStatus(); // Check system status when the button is clicked
        });
    };

    const parseCommand = (input) => {
        const args = input.split(" ").filter(arg => arg.trim() !== ""); // Split and remove empty parts
        const command = args[0].toLowerCase();

        // Log the command and arguments to debug
        console.log(`Command: ${command}, Arguments: ${JSON.stringify(args)}`);

        switch (command) {
            case "/help":
                displayHelp();
                break;

            case "/say":
                if (args.length < 2) {
                    logToTerminal("Usage: /say <message>");
                    return;
                }
                const message = args.slice(1).join(" ");
                fetch('/speech/say', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                })
                    .then(response => response.json())
                    .then(data => logToTerminal(`Bot: ${data.message}`))
                    .catch(error => logToTerminal(`Error sending message: ${error}`));
                break;

                case "/login":
                    if (args.length < 3) {
                        logToTerminal("Usage: /login <server_ip> <player_id>");
                        return;
                    }
                    const serverIp = args[1]; // Dynamically set server IP from the first argument
                    const playerId = args[2];

                    logToTerminal(`Attempting to log in to ${serverIp} as Player ${playerId}...`);

                    // Ensure the serverIp is not empty
                    if (!serverIp) {
                        logToTerminal("Server IP is not set properly. Please provide a valid server IP.");
                        return;
                    }

                    const url = (`/network/command`); 
                    const serverURL = (`http://${serverIp}/command`);


                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            command: `/login ${serverIp} ${playerId}`
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "success") {
                            logToTerminal(`Stored server IP: ${serverIp}`);
                        } else {
                            logToTerminal(`Failed to store IP: ${data.message}`);
                        }
                    })
                    .catch(error => logToTerminal(`Error logging in: ${error}`));
                    break;

            case "/disconnect":
                if (args.length < 2) {
                    logToTerminal("Usage: /disconnect <player_id>");
                    return;
                }
                const playerIdToDisconnect = args[1];

                logToTerminal(`Attempting to disconnect Player ${playerIdToDisconnect}...`);

                const disconnectUrl = `http://${serverIp}/command`;  // Same server URL

                fetch(disconnectUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        command: `/disconnect ${playerIdToDisconnect}`
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "success") {
                            logToTerminal(`Player ${playerIdToDisconnect} disconnected successfully.`);
                        } else {
                            logToTerminal(`Disconnect failed: ${data.message}`);
                        }
                    })
                    .catch(error => logToTerminal(`Error disconnecting: ${error}`));
                break;

            case "/check-system-status":
                fetchSystemStatus();
                break;

            default:
                logToTerminal(`Unknown command: ${command}. Use /help to see available commands.`);
        }
    };

    // Function to display all available commands and their descriptions
    const displayHelp = () => {
        logToTerminal(`
            <strong>Available Commands:</strong><br>
            <ul>
                <li><strong>/help</strong> - Show the list of available commands.</li>
                <li><strong>/say message</strong> - Make the robot say something via speech synthesis.</li>
                <li><strong>/login server_ip player_id</strong> - Log in to the game server as the specified player.</li>
                <li><strong>/disconnect player_id</strong> - Disconnect the player from the game server.</li>
                <li><strong>/check-system-status</strong> - Retrieve and display the system status of the robot.</li>
            </ul>
        `);
    };

    displayHelp();
    return { logToTerminal, bindTerminalEvents };
})();
