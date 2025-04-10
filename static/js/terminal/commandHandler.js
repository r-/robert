const CommandHandlers = (() => {
    const say = async (args) => {
        if (args.length < 2) {
            Terminal.logToTerminal("Usage: /say <message>");
            return;
        }
        const message = args.slice(1).join(" ");
        try {
            const response = await fetch('/speech/say', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            Terminal.logToTerminal(`Bot: ${data.message}`);
        } catch (error) {
            Terminal.logToTerminal(`Error sending message: ${error}`);
        }
    };

    const login = async (args) => {
        if (args.length < 3) {
            Terminal.logToTerminal("Usage: /login <server_ip> <player_id>");
            return;
        }
        const [_, ip, playerId] = args;
        Terminal.setServerIp(ip);

        Terminal.logToTerminal(`Attempting to log in to ${ip} as Player ${playerId}...`);

        try {
            const response = await fetch('/network/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: `/login ${ip} ${playerId}` })
            });
            const data = await response.json();

            if (data.status === "success") {
                Terminal.logToTerminal(`Stored server IP: ${ip}`);
            } else {
                Terminal.logToTerminal(`Failed to store IP: ${data.message}`);
            }
        } catch (error) {
            Terminal.logToTerminal(`Error logging in: ${error}`);
        }
    };

    const disconnect = async (args) => {
        if (args.length < 2) {
            Terminal.logToTerminal("Usage: /disconnect <player_id>");
            return;
        }
        const playerId = args[1];
        const ip = Terminal.getServerIp();
        if (!ip) {
            Terminal.logToTerminal("No server IP stored. Use /login first.");
            return;
        }

        try {
            const response = await fetch(`http://${ip}/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: `/disconnect ${playerId}` })
            });
            const data = await response.json();

            if (data.status === "success") {
                Terminal.logToTerminal(`Player ${playerId} disconnected successfully.`);
            } else {
                Terminal.logToTerminal(`Disconnect failed: ${data.message}`);
            }
        } catch (error) {
            Terminal.logToTerminal(`Error disconnecting: ${error}`);
        }
    };

    const fetchSystemStatus = async () => {
        try {
            const response = await fetch('motors/get_system_status');
            const data = await response.json();

            for (const component in data) {
                Terminal.logToTerminal(`${component}: ${data[component]}`);
            }
        } catch (error) {
            Terminal.logToTerminal(`Error fetching system status: ${error}`);
        }
    };

    const help = () => {
        Terminal.logToTerminal(`
            <strong>Available Commands:</strong><br>
            <ul>
                <li><strong>/help</strong> - Show the list of available commands.</li>
                <li><strong>/say message</strong> - Make the robot say something via speech synthesis.</li>
                <li><strong>/login server_ip player_id</strong> - Log in to the game server as the specified player.</li>
                <li><strong>/disconnect player_id</strong> - Disconnect the player from the game server.</li>
                <li><strong>/check-system-status</strong> - Retrieve and display the system status of the robot.</li>
            </ul>
        `, true);     
    };

    return {
        say,
        login,
        disconnect,
        fetchSystemStatus,
        help
    };
})();
