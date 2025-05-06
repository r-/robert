const Terminal = (() => {
    let serverIp = "";

    const escapeHtml = (unsafe) => {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    };

    const logToTerminal = (message, isHtml = false) => {
        console.log("logToTerminal called");  // Add this for debugging
        const terminal = document.getElementById("terminal");
        if (!terminal) {
            console.error("Terminal element not found!");
            return;
        }
        const content = isHtml ? message : escapeHtml(message);
        terminal.innerHTML += `<div>${content}</div>`;
        terminal.scrollTop = terminal.scrollHeight;
    };

    const setServerIp = (ip) => { serverIp = ip; };
    const getServerIp = () => serverIp;

    return {
        logToTerminal,
        setServerIp,
        getServerIp
    };
})();

console.log("terminal.js loaded");
