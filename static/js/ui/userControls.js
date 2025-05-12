const UserControls = (() => {
    let activeKeys = {};
    let cooldownInProgress = false;
    let cooldownTimer = 0;
    let cooldownInterval;

    const updateMotors = () => {
        let leftMotor = 0;
        let rightMotor = 0;
        let cameramotor = 0;

        if (activeKeys["i"] || activeKeys["k"]) {
            if (activeKeys["i"]) {
                cameramotor += 1;
            }
            if (activeKeys["k"]) {
                cameramotor -= 1;
            }
        }
        RobotApi.sendCameraCommand(cameramotor);

        // Handle horizontal movement
        if (activeKeys["ArrowUp"]) {
            leftMotor += 1;
            rightMotor += 1;
        }
        if (activeKeys["ArrowDown"]) {
            leftMotor -= 1;
            rightMotor -= 1;
        }
        if (activeKeys["ArrowLeft"]) {
            leftMotor -= 1;
            rightMotor += 1;
        }
        if (activeKeys["ArrowRight"]) {
            leftMotor += 1;
            rightMotor -= 1;
        }

        // Normalize between -1 and 1
        leftMotor = Math.max(-1, Math.min(1, leftMotor));
        rightMotor = Math.max(-1, Math.min(1, rightMotor));

        console.log(`Motors: Left=${leftMotor}, Right=${rightMotor}, Camera=${cameramotor}`);
        RobotApi.sendMotorCommand(leftMotor.toString(), rightMotor.toString());
    };

    const bindRobotControls = () => {
        document.addEventListener("keydown", (event) => {
            // Check if the active element is an input or textarea
            if (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA") {
                return; // If yes, don't process key events
            }

            if (!activeKeys[event.key]) {
                activeKeys[event.key] = true;
                console.log(`Key pressed: ${event.key}`);
                if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "i", "k"].includes(event.key)) {
                    updateMotors();
                } else if (event.key === " ") {
                    RobotApi.shoot();
                    startCooldown();
                }
            }
        });

        document.addEventListener("keyup", (event) => {
            // Check if the active element is an input or textarea
            if (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA") {
                return; // If yes, don't process key events
            }

            if (activeKeys[event.key]) {
                delete activeKeys[event.key];
                console.log(`Key released: ${event.key}`);
                if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "i", "k"].includes(event.key)) {
                    updateMotors();
                }
            }
        });
    };

    const startCooldown = () => {
        if(cooldownInProgress == true){
            return;
        }
        cooldownInProgress = true;
        cooldownTimer = 2; // 2 seconds cooldown
        updateCooldownDisplay();

        cooldownInterval = setInterval(() => {
            cooldownTimer -= 0.1; // decrease every 100ms
            if (cooldownTimer <= 0) {
                clearInterval(cooldownInterval);
                cooldownInProgress = false;
                cooldownTimer = 0;
            }
            updateCooldownDisplay();
        }, 100); // Update every 100ms
    };

    const updateCooldownDisplay = () => {
        const cooldownText = document.getElementById("cooldown-text");
        const cooldownBar = document.getElementById("cooldown-bar");

        if (cooldownText && cooldownBar) {
            cooldownText.textContent = `${cooldownTimer.toFixed(1)}s`;
            cooldownBar.value = (cooldownTimer / 2) * 100; // Map cooldown time (0 to 2 seconds) to 0 to 100
        }
    };

    return { bindRobotControls, startCooldown };
})();
