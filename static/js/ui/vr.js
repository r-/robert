// vr.js

// Variables to hold the current XR session and controller references
let xrSession = null;
let controllers = [];

// Function to enter VR mode
function enterVR() {
    if (navigator.xr) {
        // Check if WebXR is available and if the browser supports VR
        navigator.xr.requestDevice().then(device => {
            return device.requestSession('immersive-vr');  // Request immersive VR session
        }).then(session => {
            // Start the VR session
            xrSession = session;
            xrSession.addEventListener('end', onVRSessionEnd);
            xrSession.requestReferenceSpace('local').then(referenceSpace => {
                xrSession.requestAnimationFrame(onXRFrame);
            });

            document.body.classList.add('vr-mode');  // Add VR mode style to body (optional)
            console.log("Entered VR mode");
        }).catch(err => {
            console.error("Failed to start VR session:", err);
            alert("VR is not supported or there was an issue starting VR.");
        });
    } else {
        alert("WebXR is not supported on this device or browser.");
    }
}

// Function to exit VR mode
function exitVR() {
    if (xrSession) {
        xrSession.end();
        xrSession = null;
        document.body.classList.remove('vr-mode');  // Remove VR mode style
        console.log("Exited VR mode");
    }
}

// Function to handle VR frame rendering
function onXRFrame(time, frame) {
    const session = frame.session;
    const inputSources = frame.getInputSources();
    controllers = inputSources.filter(inputSource => inputSource.hand);

    // Loop through controllers to check for joystick input
    controllers.forEach(controller => {
        const gamepad = controller.gamepad;

        if (gamepad) {
            // Get joystick values (left and right thumbsticks)
            const leftJoystickX = gamepad.axes[0];  // Left thumbstick X
            const leftJoystickY = gamepad.axes[1];  // Left thumbstick Y

            // Convert joystick input into motor control signals for the robot
            const magnitude = Math.sqrt(leftJoystickX * leftJoystickX + leftJoystickY * leftJoystickY);
            if (magnitude < 0.2) {
                RobotApi.sendMotorCommand(0, 0);  // Stop robot if joystick is not moving significantly
            } else {
                const leftMotor = leftJoystickY;  // Forward/backward movement
                const rightMotor = leftJoystickX; // Left/right turning
                RobotApi.sendMotorCommand(leftMotor, rightMotor);
            }
        }
    });

    // Request the next animation frame to continue VR interaction
    session.requestAnimationFrame(onXRFrame);
}

// Function to handle when VR session ends
function onVRSessionEnd() {
    console.log("VR session has ended.");
    document.body.classList.remove('vr-mode');  // Clean up VR mode styles
}

// Event listener for VR button click
document.getElementById('enterVR').addEventListener('click', () => {
    // Check if already in VR mode, and exit if true
    if (document.body.classList.contains('vr-mode')) {
        exitVR();
    } else {
        enterVR();
    }
});
