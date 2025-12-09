/**
 * Game Output and Dojo Integration
 * Provides example commands and integration for Dojo game server
 */

console.log("gameOutput.js loaded");

// Example commands for terminal
Terminal.logToTerminal("=== R.O.B.E.R.T Dojo Game Integration ===", false);
Terminal.logToTerminal("Ready to connect to Dojo game server", false);
Terminal.logToTerminal("", false);
Terminal.logToTerminal("Available commands:", false);
Terminal.logToTerminal("  DojoApi.joinGame('http://localhost:3000', 42) - Join game with code", false);
Terminal.logToTerminal("  DojoApi.attack('targetId', 20) - Attack another player", false);
Terminal.logToTerminal("  DojoApi.obtainFlag() - Pick up the flag", false);
Terminal.logToTerminal("  DojoApi.captureFlag() - Deliver the flag", false);
Terminal.logToTerminal("  DojoApi.getEvents() - Get game events", false);
Terminal.logToTerminal("  DojoApi.getStatus() - Check connection status", false);
Terminal.logToTerminal("", false);
Terminal.logToTerminal("⚡ Ready for battle!", false);