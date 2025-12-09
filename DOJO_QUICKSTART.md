# Dojo Integration Quick Start

## What's New

R.O.B.E.R.T is now fully compatible with the Dojo game server! Your robot can now:
- ✅ Join multiplayer games
- ✅ Attack other players
- ✅ Obtain and capture flags
- ✅ See real-time game updates in the terminal

## Quick Setup

### 1. Start Your Dojo Server
```bash
# Run Dojo on port 3000 (or whatever port you choose)
node dojo-server.js
```

### 2. Connect R.O.B.E.R.T
In the browser console or terminal interface, run:

```javascript
DojoApi.joinGame('http://localhost:3000', 42)
```

That's it! Replace:
- `http://localhost:3000` with your Dojo server URL
- `42` with your player code (0-99)

### 3. Play the Game!

```javascript
// Attack someone
DojoApi.attack('enemy-player-id', 20)

// Get the flag
DojoApi.obtainFlag()

// Win the game!
DojoApi.captureFlag()
```

## What Happens Automatically

✅ **On Join:**
- Your player ID is registered
- Event streaming starts
- Terminal shows real-time updates

✅ **During Game:**
- Terminal updates every 1 second with new events
- Shows player actions (attacks, flag events, etc.)
- Timestamps on all messages
- Error alerts if something goes wrong

## Terminal Output

You'll see something like:
```
[14:23:46] ✅ Joined game! Player ID: abc123
[14:23:47] Starting event stream from Dojo server...
[14:23:50] player_joined: Player 42 joined the game
[14:23:55] 🚩 Flag spawned at base
[14:24:00] ⚔️ Attack successful!
[14:24:10] 🎉 Flag captured! Victory!
```

## Available Commands

```javascript
// Join game
DojoApi.joinGame(serverUrl, playerCode)

// Game actions
DojoApi.attack(targetId, damage)
DojoApi.obtainFlag()
DojoApi.captureFlag()

// Monitoring
DojoApi.getEvents()
DojoApi.getStatus()

// Terminal control
Terminal.startEventStream()
Terminal.stopEventStream()
Terminal.logToTerminal("Message")
```

## Shooting Integration

Combine Dojo gameplay with physical shooting:

```javascript
// Attack and shoot simultaneously
DojoApi.attack(targetId, 20)
RobotApi.shoot()  // Fires the shooting mechanism!
```

## Troubleshooting

### "Not connected to Dojo server"
→ Call `DojoApi.joinGame()` first

### Events not updating?
→ Check `DojoApi.getStatus()` - are you still connected?

### Server connection timeout?
→ Make sure Dojo server is running and reachable

### Player code rejected?
→ Code must be 0-99. Try a different number.

## API Details

Complete API documentation: `DOJO_INTEGRATION.md`

Implementation details: `DOJO_IMPLEMENTATION.md`

## Architecture

```
Browser
    ↓
RobotApi (existing)
    ↓
DojoApi (new)
    ↓
Flask Backend (/dojo endpoints)
    ↓
Dojo Game Server
```

## Files Changed/Added

**New:**
- `routes/dojo.py` - Backend Dojo integration
- `static/js/api/dojoApi.js` - Frontend API client
- `DOJO_INTEGRATION.md` - Complete documentation
- `DOJO_IMPLEMENTATION.md` - Technical details

**Updated:**
- `app.py` - Register Dojo blueprint
- `routes/network.py` - Track player state
- `static/js/terminal/terminal.js` - Real-time streaming
- `static/js/terminal/gameOutput.js` - Example commands

## Next Steps

1. ✅ R.O.B.E.R.T code is ready
2. 🔧 Start your Dojo server
3. 🎮 Join a game with `DojoApi.joinGame()`
4. 🎯 Start playing!

## Support

For detailed information:
- Game mechanics: `DOJO_INTEGRATION.md`
- Implementation details: `DOJO_IMPLEMENTATION.md`
- API specification: Dojo server `/docs.html`
