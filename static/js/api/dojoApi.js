/**
 * Dojo Game Server API Client
 * Handles all communication with the Dojo game server
 */

const DojoApi = (() => {
    /**
     * Join a Dojo game server
     * @param {string} serverUrl - URL of the Dojo server (e.g., http://localhost:3000)
     * @param {number} playerCode - Player code (0-99)
     */
    const joinGame = (serverUrl, playerCode) => {
        console.log(`Joining Dojo game: ${serverUrl} with code ${playerCode}`);

        const data = JSON.stringify({ server_url: serverUrl, code: playerCode });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/dojo/join", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Join response:", response);
                    Terminal.logToTerminal(`✅ Joined game! Player ID: ${response.player_id}`, false);
                    Terminal.setDojoServer(serverUrl);
                    Terminal.startEventStream();
                } else {
                    const error = JSON.parse(xhr.responseText);
                    console.error("Join error:", error);
                    Terminal.logToTerminal(`❌ Failed to join: ${error.message}`, false);
                }
            }
        };

        xhr.send(data);
    };

    /**
     * Attack another player
     * @param {string} targetId - ID of the player to attack
     * @param {number} damage - Damage amount (optional, default 20)
     */
    const attack = (targetId, damage = 20) => {
        console.log(`Attacking player ${targetId} for ${damage} damage`);

        const data = JSON.stringify({ damage });

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/dojo/attack/${targetId}`, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Attack response:", response);
                    Terminal.logToTerminal(`⚔️ Attack successful!`, false);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    console.error("Attack error:", error);
                    Terminal.logToTerminal(`❌ Attack failed: ${error.message}`, false);
                }
            }
        };

        xhr.send(data);
    };

    /**
     * Obtain/steal the flag
     */
    const obtainFlag = () => {
        console.log("Attempting to obtain flag");

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/dojo/flag/obtain", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Flag obtain response:", response);
                    Terminal.logToTerminal(`🚩 Flag obtained!`, false);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    console.error("Flag obtain error:", error);
                    Terminal.logToTerminal(`❌ Cannot obtain flag: ${error.message}`, false);
                }
            }
        };

        xhr.send(JSON.stringify({}));
    };

    /**
     * Capture/deliver the flag
     */
    const captureFlag = () => {
        console.log("Attempting to capture flag");

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/dojo/flag/capture", true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Flag capture response:", response);
                    Terminal.logToTerminal(`🎉 Flag captured! Victory!`, false);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    console.error("Flag capture error:", error);
                    Terminal.logToTerminal(`❌ Cannot capture flag: ${error.message}`, false);
                }
            }
        };

        xhr.send(JSON.stringify({}));
    };

    /**
     * Get current game events
     */
    const getEvents = () => {
        console.log("Getting game events");

        const xhr = new XMLHttpRequest();
        xhr.open("GET", "/dojo/events", true);

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Events response:", response);
                    Terminal.logToTerminal(`📊 Retrieved ${response.events.length} events`, false);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    console.error("Events error:", error);
                    Terminal.logToTerminal(`❌ Cannot get events: ${error.message}`, false);
                }
            }
        };

        xhr.send();
    };

    /**
     * Get connection status
     */
    const getStatus = () => {
        console.log("Getting Dojo connection status");

        const xhr = new XMLHttpRequest();
        xhr.open("GET", "/dojo/status", true);

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log("Status response:", response);
                    const status = response.status === "connected" ? "✅ Connected" : "❌ Disconnected";
                    Terminal.logToTerminal(`${status} to Dojo server`, false);
                } else {
                    console.error("Status error");
                    Terminal.logToTerminal(`❌ Cannot get status`, false);
                }
            }
        };

        xhr.send();
    };

    return {
        joinGame,
        attack,
        obtainFlag,
        captureFlag,
        getEvents,
        getStatus
    };
})();

console.log("DojoApi loaded");
