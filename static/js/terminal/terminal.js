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
        const terminal = document.getElementById("terminal");
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
