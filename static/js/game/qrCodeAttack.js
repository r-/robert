/**
 * QR Code Attack System for Dojo
 * 
 * When camera detects a QR code:
 * - If it's a player ID (0-99 except 0,1): Attack them
 * - If it's a flag ID (0 or 1): Capture the flag
 */

const QRCodeAttackSystem = (() => {
    let lastAttackedId = null;
    let lastAttackTime = 0;
    const ATTACK_COOLDOWN = 500; // ms between attacks on same target
    const FLAG_COOLDOWN = 2000; // ms between flag captures

    /**
     * Handle detected QR code
     * @param {string} qrCodeData - Content of QR code
     */
    const handleDetectedQR = async (qrCodeData) => {
        if (!DojoGame.isConnected()) {
            return; // Not connected to game, ignore QR codes
        }

        try {
            const targetId = parseInt(qrCodeData);

            if (isNaN(targetId) || targetId < 0 || targetId > 99) {
                return; // Invalid ID
            }

            const now = Date.now();

            // Handle flag (ID 0 or 1)
            if (targetId === 0 || targetId === 1) {
                if (now - lastAttackTime >= FLAG_COOLDOWN) {
                    Terminal.logToTerminal(`🚩 Flag detected: ID ${targetId}`);
                    await DojoGame.obtainFlag(targetId);
                    lastAttackTime = now;
                }
                return;
            }

            // Handle player attack
            if (lastAttackedId === targetId && now - lastAttackTime < ATTACK_COOLDOWN) {
                return; // Too soon to attack same player again
            }

            Terminal.logToTerminal(`📍 Target detected: Player ${targetId}`);
            await DojoGame.attackPlayer(targetId);
            
            lastAttackedId = targetId;
            lastAttackTime = now;

        } catch (error) {
            console.error("Error in QR attack system:", error);
        }
    };

    /**
     * Check if ready to attack (respects cooldown)
     */
    const isReadyToAttack = () => {
        return Date.now() - lastAttackTime >= ATTACK_COOLDOWN;
    };

    /**
     * Reset cooldown (useful for testing)
     */
    const resetCooldown = () => {
        lastAttackTime = 0;
        lastAttackedId = null;
    };

    return {
        handleDetectedQR,
        isReadyToAttack,
        resetCooldown
    };
})();
