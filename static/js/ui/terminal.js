const Terminal = (() => {
    let serverIp = ""; // Dynamically set server IP

    const logToTerminal = (message) => {
        const terminal = document.getElementById("terminal");
        terminal.innerHTML += `<div>${message}</div>`;
        terminal.scrollTop = terminal.scrollHeight;
    };

    const fetchSystemStatus = () => {
        fetch('/get_system_status')
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

    return { logToTerminal, bindTerminalEvents };
})();
