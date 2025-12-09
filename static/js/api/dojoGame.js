/**
 * Dojo Game Client - Simplified QR-code based attack system
 * 
 * Usage:
 *   DojoGame.setConnection(serverUrl, playerId, playerCode)
 *   DojoGame.attackPlayer(targetId)
 *   DojoGame.obtainFlag(flagId)  // flagId = 0 or 1
 *   DojoGame.captureFlag()
 */

const DojoGame = (() => {
    let serverUrl = null;
    let playerId = null;
    let playerCode = null;

    const setConnection = (url, id, code) => {
        serverUrl = url.endsWith('/') ? url.slice(0, -1) : url;
        playerId = id;
        playerCode = code;
        console.log(`🎮 Dojo Game initialized: Player ${id} (Code: ${code}) on ${serverUrl}`);
    };

    const isConnected = () => {
        return serverUrl !== null && playerId !== null;
    };

    const getConnection = () => {
        return {
            connected: isConnected(),
            serverUrl,
            playerId,
            playerCode
        };
    };

    /**
     * Attack a player by their QR code ID
     * @param {number} targetId - Player ID from QR code (0-99)
     * @param {number} damage - Damage amount (default 20)
     */
    const attackPlayer = async (targetId, damage = 20) => {
        if (!isConnected()) {
            Terminal.logToTerminal("❌ Not connected to Dojo server. Use /JoinGame first.");
            return false;
        }

        try {
            const response = await fetch(`/dojo/attack/${targetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ damage })
            });

            const data = await response.json();

            if (response.ok) {
                Terminal.logToTerminal(`⚔️ ${data.message}`);
                RobotApi.shoot(); // Fire the shooting mechanism!
                return true;
            } else {
                Terminal.logToTerminal(`❌ ${data.message}`);
                return false;
            }
        } catch (error) {
            Terminal.logToTerminal(`❌ Attack failed: ${error.message}`);
            return false;
        }
    };

    /**
     * Obtain a flag from the game
     * @param {number} flagId - Flag ID (0 or 1 for team flags)
     */
    const obtainFlag = async (flagId) => {
        if (!isConnected()) {
            Terminal.logToTerminal("❌ Not connected to Dojo server. Use /JoinGame first.");
            return false;
        }

        if (flagId !== 0 && flagId !== 1) {
            Terminal.logToTerminal("❌ Flag ID must be 0 or 1");
            return false;
        }

        try {
            const response = await fetch(`/dojo/flag/${flagId}/obtain`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (response.ok) {
                Terminal.logToTerminal(`🚩 ${data.message}`);
                return true;
            } else {
                Terminal.logToTerminal(`❌ ${data.message}`);
                return false;
            }
        } catch (error) {
            Terminal.logToTerminal(`❌ Flag obtain failed: ${error.message}`);
            return false;
        }
    };

    /**
     * Capture (deliver) the flag to win the game
     */
    const captureFlag = async () => {
        if (!isConnected()) {
            Terminal.logToTerminal("❌ Not connected to Dojo server. Use /JoinGame first.");
            return false;
        }

        try {
            const response = await fetch('/dojo/flag/capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (response.ok) {
                Terminal.logToTerminal(`🎉 ${data.message}`);
                return true;
            } else {
                Terminal.logToTerminal(`❌ ${data.message}`);
                return false;
            }
        } catch (error) {
            Terminal.logToTerminal(`❌ Flag capture failed: ${error.message}`);
            return false;
        }
    };

    /**
     * Get game events from server
     */
    const getEvents = async () => {
        if (!isConnected()) {
            return [];
        }

        try {
            const response = await fetch('/dojo/events', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                return data.events || [];
            }
            return [];
        } catch (error) {
            console.error("Error getting events:", error);
            return [];
        }
    };

    /**
     * Get connection status
     */
    const getStatus = async () => {
        try {
            const response = await fetch('/dojo/status', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error("Error getting status:", error);
            return null;
        }
    };

    return {
        setConnection,
        isConnected,
        getConnection,
        attackPlayer,
        obtainFlag,
        captureFlag,
        getEvents,
        getStatus
    };
})();
