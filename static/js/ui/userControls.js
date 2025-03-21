const UserControls = (() => {
    let activeKeys = {};

    const updateMotors = () => {
        let leftMotor = 0;
        let rightMotor = 0;

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

        console.log(`Motors: Left=${leftMotor}, Right=${rightMotor}`);
        RobotApi.sendMotorCommand(leftMotor.toString(), rightMotor.toString());
    };

    const bindRobotControls = () => {
        document.addEventListener("keydown", (event) => {
            if (!activeKeys[event.key]) {
                activeKeys[event.key] = true;
                console.log(`Key pressed: ${event.key}`);
                if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
                    updateMotors();
                } else if (event.key === " ") {
                    RobotApi.activate();
                }
            }
        });

        document.addEventListener("keyup", (event) => {
            if (activeKeys[event.key]) {
                delete activeKeys[event.key];
                console.log(`Key released: ${event.key}`);
                if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
                    updateMotors();
                }
            }
        });
    };

    return { bindRobotControls };
})();
