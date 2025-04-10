const UIBinder = (() => {
    const bindEvents = () => {
        const input = document.getElementById("command-input");
        const sendBtn = document.getElementById("send-command");
        const checkBtn = document.getElementById("check-system-status");

        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                const value = input.value.trim();
                input.value = "";
                CommandParser.parseCommand(value);
            }
        });

        sendBtn.addEventListener("click", () => {
            const value = input.value.trim();
            input.value = "";
            CommandParser.parseCommand(value);
        });

        checkBtn.addEventListener("click", CommandHandlers.fetchSystemStatus);
    };

    return { bindEvents };
})();
