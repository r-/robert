const Terminal = (() => {
    let serverIp = "";
    let dojoServer = null;
    let eventSource = null;

    const escapeHtml = (unsafe) => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    };

    const logToTerminal = (message, isHtml = false) => {
        console.log("logToTerminal called with:", message);
        const terminal = document.getElementById("terminal");
        if (!terminal) {
            console.error("Terminal element not found!");
            return;
        }
        
        // Format with timestamp
        const timestamp = new Date().toLocaleTimeString();
        const content = isHtml ? message : escapeHtml(String(message));
        terminal.innerHTML += `<div><span style="color: #999;">[${timestamp}]</span> ${content}</div>`;
        terminal.scrollTop = terminal.scrollHeight;
    };

    const setServerIp = (ip) => { 
        serverIp = ip;
        logToTerminal(`Server IP set: ${ip}`);
    };
    
    const getServerIp = () => serverIp;

    const setDojoServer = (url) => {
        dojoServer = url;
        logToTerminal(`Dojo Server: ${url}`);
    };

    const getDojoServer = () => dojoServer;

    const startEventStream = () => {
        if (!eventSource) {
            logToTerminal("Starting event stream from Dojo server...");
            eventSource = new EventSource("/dojo/events/stream");
            
            eventSource.onmessage = (event) => {
                try {
                    const eventData = JSON.parse(event.data);
                    
                    if (eventData.error) {
                        logToTerminal(`⚠️ Error: ${eventData.error}`, false);
                    } else {
                        const msg = `${eventData.type}: ${eventData.message}`;
                        logToTerminal(msg, false);
                    }
                } catch (e) {
                    console.error("Error parsing event:", e);
                }
            };
            
            eventSource.onerror = (error) => {
                logToTerminal("❌ Event stream error", false);
                console.error("EventSource error:", error);
                if (eventSource.readyState === EventSource.CLOSED) {
                    logToTerminal("⚠️ Event stream disconnected", false);
                }
            };
        }
    };

    const stopEventStream = () => {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
            logToTerminal("Event stream stopped");
        }
    };

    return {
        logToTerminal,
        setServerIp,
        getServerIp,
        setDojoServer,
        getDojoServer,
        startEventStream,
        stopEventStream
    };
})();

console.log("terminal.js loaded");
