# R.O.B.E.R.T Dojo Game Server Integration

## Overview

R.O.B.E.R.T is now fully compatible with the Dojo game server. This integration allows the robot to:
- Join multiplayer games with a player code
- Attack other players
- Obtain and capture the flag
- Receive real-time game events in the terminal

## Quick Start

### 1. Join a Game

```javascript
// Join Dojo server running on localhost:3000 with player code 42
DojoApi.joinGame('http://localhost:3000', 42);
```

This will:
- Register R.O.B.E.R.T with the game server
- Display your player ID in the terminal
- Start streaming live game events
- Begin listening for real-time updates

### 2. Play the Game

```javascript
// Attack another player
DojoApi.attack('target-player-id', 20);  // 20 damage

// Obtain the flag
DojoApi.obtainFlag();

// Capture the flag (win the game!)
DojoApi.captureFlag();
```

### 3. Monitor Game State

```javascript
// Get current events
DojoApi.getEvents();

// Check connection status
DojoApi.getStatus();
```

## API Endpoints

All endpoints are prefixed with `/dojo`:

### POST /dojo/join
**Join a Dojo game server**

Request:
```json
{
  "server_url": "http://localhost:3000",
  "code": 42
}
```

Response:
```json
{
  "status": "success",
  "player_id": "player-uuid",
  "message": "Joined game with code 42"
}
```

### POST /dojo/attack/:target_id
**Attack another player**

Request:
```json
{
  "damage": 20
}
```

Response:
```json
{
  "status": "success",
  "message": "Attacked player target-id",
  "server_response": {...}
}
```

### POST /dojo/flag/obtain
**Pick up the flag**

Request: (empty body)

Response:
```json
{
  "status": "success",
  "message": "Flag obtained!",
  "server_response": {...}
}
```

### POST /dojo/flag/capture
**Deliver the flag (win!)**

Request: (empty body)

Response:
```json
{
  "status": "success",
  "message": "Flag captured!",
  "server_response": {...}
}
```

### GET /dojo/events
**Get all game events**

Response:
```json
{
  "status": "success",
  "events": [
    {
      "type": "player_joined",
      "message": "Player 42 joined",
      "timestamp": 1702100000
    },
    ...
  ]
}
```

### GET /dojo/events/stream
**Stream events via Server-Sent Events (SSE)**

Continuously streams game events to keep the terminal updated in real-time.

**Format:**
```
data: {"type": "player_attacked", "message": "...", "timestamp": ...}

data: {"type": "flag_obtained", "message": "...", "timestamp": ...}
```

### GET /dojo/status
**Get R.O.B.E.R.T connection status**

Response:
```json
{
  "status": "connected",
  "server_url": "http://localhost:3000",
  "player_id": "player-uuid",
  "timestamp": 1702100000
}
```

## Terminal Integration

The terminal automatically:
1. **Displays connection status** when joining a game
2. **Shows timestamps** for all events
3. **Streams live updates** from the Dojo server
4. **Logs all actions** (attacks, flag events, errors)

### Terminal Commands

```javascript
// In browser console or terminal interface
Terminal.logToTerminal("Custom message");
Terminal.setDojoServer("http://localhost:3000");
Terminal.startEventStream();
Terminal.stopEventStream();
Terminal.getDojoServer();
```

## Example Game Flow

```javascript
// 1. Join game
DojoApi.joinGame('http://localhost:3000', 5);
// Terminal shows: "✅ Joined game! Player ID: abc123"
// Terminal starts streaming events

// 2. Wait for flag to appear (see in terminal)
// Terminal shows: "🚩 Flag spawned at base"

// 3. Obtain flag
DojoApi.obtainFlag();
// Terminal shows: "🚩 Flag obtained!"

// 4. Navigate to enemy base and attack defenders
DojoApi.attack('enemy-player-1', 20);
// Terminal shows: "⚔️ Attack successful!"

// 5. Capture flag to win
DojoApi.captureFlag();
// Terminal shows: "🎉 Flag captured! Victory!"
```

## Error Handling

All errors are logged to the terminal with clear messages:

```
❌ Failed to join: Player code must be between 0 and 99
❌ Attack failed: Server error: 400
⚠️ Error: Connection timeout
❌ Cannot obtain flag: Flag is not available
```

## Real-Time Event Stream

The event stream provides real-time updates:

```
[12:34:56] ✅ Joined game! Player ID: abc123
[12:34:57] 📊 Event stream started
[12:35:00] player_joined: Player 42 joined the game
[12:35:05] 🚩 Flag spawned at base
[12:35:10] player_moved: Player abc123 moved
[12:35:15] flag_obtained: Player abc123 obtained flag
[12:35:20] flag_captured: Player abc123 captured flag! Blue team wins!
```

## Configuration

### Server URL
- Dojo server must be accessible from the robot's network
- Default: `http://localhost:3000`
- Can be any reachable Dojo server instance

### Player Code
- Must be a number between 0 and 99
- Determines player assignment in the game
- Server-side configuration determines team placement

## Troubleshooting

### "Not connected to Dojo server"
- Call `DojoApi.joinGame()` first to establish connection
- Check that Dojo server URL is correct and server is running

### "Connection timeout"
- Verify Dojo server is running on the specified address
- Check network connectivity
- Verify firewall allows connection to Dojo server port

### Events not updating
- Check that event stream is running: `DojoApi.getStatus()`
- Open browser console for error messages
- Dojo server may be disconnected

### Player code rejected
- Player code must be 0-99
- Check server-side player limit configuration
- Try a different player code

## Integration with R.O.B.E.R.T Hardware

When you call `DojoApi.attack()`, you can also trigger the physical shooting mechanism:

```javascript
// Attack and shoot simultaneously
DojoApi.attack(targetId, 20);
RobotApi.shoot();  // Fires the shooting mechanism
```

This allows the robot to physically respond to game actions!

## Notes

- All data is in-memory on the Dojo server
- Connection is re-established if needed
- Events are pulled from server (not pushed)
- Real-time updates happen every 1 second
- Maximum 5 connection errors before stream stops

## Future Enhancements

- WebSocket support for true real-time updates
- Team-based gameplay integration
- Score visualization in terminal
- Player radar/location tracking
- Advanced weapon/ability system
