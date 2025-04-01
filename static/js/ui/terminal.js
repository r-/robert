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
        const args = input.split(" ");
        const command = args[0].toLowerCase();

        switch (command) {
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
                serverIp = args[1];
                const playerId = args[2];

                logToTerminal(`Attempting to log in to ${serverIp} as Player ${playerId}...`);

                fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ server_ip: serverIp, player_id: playerId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        logToTerminal(`Logged in successfully as Player ${playerId}`);
                    } else {
                        logToTerminal(`Login failed: ${data.message}`);
                    }
                })
                .catch(error => logToTerminal(`Error logging in: ${error}`));
                break;

            default:
                logToTerminal(`Unknown command: ${command}`);
        }
    };

    return { logToTerminal, bindTerminalEvents };
})();
