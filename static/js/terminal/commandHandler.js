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

    const joinGame = async (args) => {
        if (args.length < 3) {
            Terminal.logToTerminal("Usage: /JoinGame <server_url:port> <player_code>");
            Terminal.logToTerminal("Example: /JoinGame localhost:3000 42");
            return;
        }

        const serverUrl = args[1];
        const playerCode = parseInt(args[2]);

        if (isNaN(playerCode) || playerCode < 0 || playerCode > 99) {
            Terminal.logToTerminal("❌ Player code must be between 0 and 99");
            return;
        }

        Terminal.logToTerminal(`🔗 Connecting to Dojo server at ${serverUrl} with code ${playerCode}...`);

        try {
            // Call backend to join game
            const response = await fetch('/dojo/status', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                Terminal.logToTerminal("❌ Failed to check Dojo status");
                return;
            }

            // Store the server URL and code in the Dojo module
            const fullUrl = serverUrl.includes('http') ? serverUrl : `http://${serverUrl}`;
            
            // Try to join via the JavaScript module
            try {
                const joinResponse = await fetch(fullUrl + '/api/player/join', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: playerCode })
                });

                if (joinResponse.ok) {
                    const joinData = await joinResponse.json();
                    const playerId = joinData.playerId || joinData.id;
                    
                    // Store in dojo module
                    if (window.DojoGame) {
                        window.DojoGame.setConnection(fullUrl, playerId, playerCode);
                    }
                    
                    Terminal.logToTerminal(`✅ Successfully joined game!`);
                    Terminal.logToTerminal(`   Player ID: ${playerId}`);
                    Terminal.logToTerminal(`   Player Code: ${playerCode}`);
                    Terminal.logToTerminal(`   Server: ${fullUrl}`);
                    Terminal.logToTerminal(`\n📸 Point camera at opponent QR codes to attack them!`);
                    Terminal.logToTerminal(`🚩 Point camera at flags (ID 0 or 1) to capture them!`);
                } else {
                    const error = await joinResponse.json();
                    Terminal.logToTerminal(`❌ Failed to join: ${error.message || 'Unknown error'}`);
                }
            } catch (err) {
                Terminal.logToTerminal(`❌ Connection error: ${err.message}`);
            }
        } catch (error) {
            Terminal.logToTerminal(`Error: ${error}`);
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
                <li><strong>/JoinGame &lt;server_url:port&gt; &lt;player_code&gt;</strong> - Join a Dojo game server (code 0-99).</li>
                <li><strong>/say message</strong> - Make the robot say something via speech synthesis.</li>
                <li><strong>/login server_ip player_id</strong> - Log in to the game server as the specified player.</li>
                <li><strong>/disconnect player_id</strong> - Disconnect the player from the game server.</li>
                <li><strong>/check-system-status</strong> - Retrieve and display the system status of the robot.</li>
            </ul>
        `, true);     
    };

    const test = () => {
        Terminal.logToTerminal(`Test IDK`, true);
    }
    return {
        say,
        joinGame,
        login,
        disconnect,
        fetchSystemStatus,
        help,
        test
    };
})();