const GameServerApi = (() => {
    let serverIp = ""; // Store the server IP

    const setServerIp = (ip) => {
        serverIp = ip; // Update the server IP
    };

    const connect = (id) => {
        return sendCommand(`/login ${serverIp} ${id}`);
    };

    const sendCommand = (command) => {
        return new Promise((resolve, reject) => {
            if (!serverIp) {
                return reject(new Error("Server IP is not set."));
            }

            // Ensure the command starts with a "/"
            if (!command.startsWith("/")) {
                command = `/${command}`;
            }

            const xhr = new XMLHttpRequest();
            xhr.open("POST", `http://${serverIp}:5001/command`, true); // Add port 5001
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        console.log(response)
                        if (response.status === "success") {
                            resolve(response);
                        } else {
                            reject(new Error(response.message));
                        }
                    } else {
                        reject(new Error(`HTTP Error: ${xhr.status} - ${xhr.statusText}`));
                    }
                }
            };

            xhr.send(JSON.stringify({ command }));
        });
    };

    return { setServerIp, connect, sendCommand };
})();
