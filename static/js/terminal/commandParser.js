const CommandParser = (() => {
    const parseCommand = (input) => {
        const args = input.trim().split(/\s+/);
        const command = args[0].toLowerCase();

        console.log(`Command: ${command}, Arguments: ${JSON.stringify(args)}`);

        switch (command) {
            case "/help": return CommandHandlers.help();
            case "/say": return CommandHandlers.say(args);
            case "/login": return CommandHandlers.login(args);
            case "/disconnect": return CommandHandlers.disconnect(args);
            case "/check-system-status": return CommandHandlers.fetchSystemStatus();
            case "/test": return CommandHandlers.test();
            default:
                Terminal.logToTerminal(`Unknown command: ${command}. Use /help to see available commands.`);
        }
    };

    return { parseCommand };
})();
