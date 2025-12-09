class GamepadController {
    constructor() {
        this.gamepads = [];
        this.neutralThreshold = 0.1; // Threshold for joystick neutral position
        this.pollInterval = 20; // Interval (in ms) for reading joystick input
        this.changeThreshold = 0.01; // Minimum change required to send a new command
        this.smoothingFactor = 0.1; // Factor to smooth snapped signals
        this.lastAxes = { x: 0, y: 0 }; // Last processed axes values
        this.lastMotorState = { forward: 0, right: 0 }; // Last sent motor state
        this.analogController = true; // Assume analog until detected otherwise
        this.init();
    }

    init() {
        window.addEventListener('gamepadconnected', (e) => this.onGamepadConnected(e));
        window.addEventListener('gamepaddisconnected', (e) => this.onGamepadDisconnected(e));
        this.startPolling();
    }

    onGamepadConnected(event) {
        console.log(`🎮 Gamepad connected: ${event.gamepad.id}`);
        console.log("💡 If the robot does not move smoothly, ensure the gamepad is in **analog mode**.");
        this.gamepads[event.gamepad.index] = event.gamepad;
    }

    onGamepadDisconnected(event) {
        console.log(`❌ Gamepad disconnected: ${event.gamepad.id}`);
        delete this.gamepads[event.gamepad.index];
    }

    startPolling() {
        setInterval(() => {
            this.updateGamepads();
            this.handleJoystickInput();
            this.handleButtonInput();
        }, this.pollInterval);
    }

    updateGamepads() {
        const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
        this.gamepads = Array.from(gamepads).filter((gp) => gp !== null);
    }

    handleJoystickInput() {
        this.gamepads.forEach((gamepad) => {
            const rawX = gamepad.axes[0];
            const rawY = gamepad.axes[1];
            console.log("raw: " , rawX , rawY)

            // Detect analog or digital mode
            this.detectAnalogSupport(gamepad);

            // Apply smoothing if controller does not support analog input
            const processedX = this.analogController ? rawX : this.smoothValue(rawX, this.lastAxes.x);
            const processedY = this.analogController ? rawY : this.smoothValue(rawY, this.lastAxes.y);

            // Update last processed axes
            this.lastAxes = { x: processedX, y: processedY };

            // Normalize joystick values (apply dead zone)
            const normalizedX = Math.abs(processedX) > this.neutralThreshold ? processedX : 0;
            const normalizedY = Math.abs(processedY) > this.neutralThreshold ? processedY : 0;

            // Convert from left/right motor speeds to forward/right control
            // Original: speedLeft = normalizedY - normalizedX, speedRight = normalizedY + normalizedX
            // Solving for normalizedY and normalizedX:
            // normalizedY = (speedLeft + speedRight) / 2 = forward
            // normalizedX = (speedRight - speedLeft) / 2 = right
            
            const forward = normalizedY;
            const right = normalizedX;

            // Ensure speeds are within the range [-1, 1]
            const clampedForward = -Math.max(-1, Math.min(1, forward));
            const clampedRight = -Math.max(-1, Math.min(1, right));

            // Send command if speeds have changed significantly
            this.sendMotorCommandIfChanged(clampedForward, clampedRight);
        });
    }

    detectAnalogSupport(gamepad) {
        // Check if all axes report either -1, 0, or 1
        const isSnapped = gamepad.axes.every((axis) => axis === -1 || axis === 0 || axis === 1);

        if (isSnapped && this.analogController) {
            console.warn(
                `⚠️ Warning: Gamepad "${gamepad.id}" appears to be in digital mode. Switch to **analog mode** for smooth control.`
            );
            this.analogController = false;
        } else if (!isSnapped && !this.analogController) {
            console.log(`🎉 Gamepad "${gamepad.id}" detected in analog mode.`);
            this.analogController = true;
        }
    }

    smoothValue(rawValue, lastValue) {
        return lastValue + (rawValue - lastValue) * this.smoothingFactor;
    }

    sendMotorCommandIfChanged(forward, right) {
        const changeForward = Math.abs(forward - this.lastMotorState.forward);
        const changeRight = Math.abs(right - this.lastMotorState.right);

        if (changeForward > this.changeThreshold || changeRight > this.changeThreshold) {
            // Send the motor command to the Flask server
            RobotApi.sendMotorCommand(forward, right);

            // Update the last motor state
            this.lastMotorState = { forward, right };

            console.log(`🚀 Motor Command Sent: Forward=${forward.toFixed(2)}, Right=${right.toFixed(2)}`);
        }
    }

    handleButtonInput(){
        this.gamepads.forEach((gamepad) => {
            if (gamepad.axes[5] > 0.8){
                console.log("shots fired");
                RobotApi.shoot()
                UserControls.startCooldown()
            }
        })
    }

    /*
    //Used the already implemented api instead in robotApi
    sendMotorCommand(left, right) {
        const motorSpeeds = { left, right };

        const xhr = new XMLHttpRequest();
        xhr.open("POST", `http://${server_ip}:5000/control_motor`, true);
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log("✅ Flask Server Response:", JSON.parse(xhr.responseText));
                } else {
                    console.error(`❌ Motor API Error: ${xhr.status} - ${xhr.statusText}`);
                }
            }
        };

        xhr.send(JSON.stringify(motorSpeeds));
    }
    */
}

document.addEventListener('DOMContentLoaded', () => {
    new GamepadController();
});
