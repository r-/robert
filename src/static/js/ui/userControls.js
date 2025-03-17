const UserControls = (() => {
    let activeKeys = {};

    const bindRobotControls = () => {
        document.addEventListener("keydown", (event) => {
            if (!activeKeys[event.key]) {
                activeKeys[event.key] = true;
                console.log(`Key pressed: ${event.key}`); // Debug log
                switch (event.key) {
                    case "ArrowUp":
                        RobotApi.sendMotorCommand("1", "1");
                        break;
                    case "ArrowDown":
                        RobotApi.sendMotorCommand("-1", "-1");
                        break;
                    case "ArrowLeft":
                        RobotApi.sendMotorCommand("-1", "1");
                        break;
                    case "ArrowRight":
                        RobotApi.sendMotorCommand("1", "-1");
                        break;
                    case " ":
                        RobotApi.activate();
                        break;
                }
            }
        });

        document.addEventListener("keyup", (event) => {
            if (activeKeys[event.key]) {
                delete activeKeys[event.key];
                console.log(`Key released: ${event.key}`); // Debug log
                switch (event.key) {
                    case "ArrowUp":
                    case "ArrowDown":
                    case "ArrowLeft":
                    case "ArrowRight":
                        RobotApi.sendMotorCommand("0", "0");
                        break;
                }
            }
        });
    };

    return { bindRobotControls };
})();
