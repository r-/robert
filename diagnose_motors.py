#!/usr/bin/env python3
"""
Motor Diagnostic Script for R.O.B.E.R.T

This script helps diagnose motor connection and initialization issues.
"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def check_buildhat_library():
    """Check if buildhat library is installed."""
    logger.info("=" * 60)
    logger.info("Checking buildhat library installation...")
    logger.info("=" * 60)
    
    try:
        import buildhat
        logger.info("✅ buildhat library is installed")
        logger.info(f"   Location: {buildhat.__file__}")
        return True
    except ImportError as e:
        logger.error("❌ buildhat library is NOT installed")
        logger.error(f"   Error: {e}")
        logger.error("\n   To install, run:")
        logger.error("   pip install buildhat")
        return False

def check_motor_detection():
    """Attempt to detect and initialize motors."""
    logger.info("\n" + "=" * 60)
    logger.info("Attempting to detect motors...")
    logger.info("=" * 60)
    
    try:
        from buildhat import Motor
        
        ports = ['A', 'B', 'C', 'D']
        detected_motors = {}
        
        for port in ports:
            try:
                logger.info(f"\nTrying motor on port {port}...")
                motor = Motor(port)
                logger.info(f"✅ Motor detected on port {port}")
                detected_motors[port] = motor
            except Exception as e:
                logger.warning(f"❌ No motor on port {port}: {type(e).__name__}: {e}")
        
        if detected_motors:
            logger.info(f"\n✅ Found {len(detected_motors)} motor(s)")
            for port, motor in detected_motors.items():
                logger.info(f"   - Port {port}: {motor}")
            return detected_motors
        else:
            logger.error("\n❌ No motors detected on any port")
            logger.error("\n   Possible causes:")
            logger.error("   1. BuildHAT is not connected to Raspberry Pi")
            logger.error("   2. Motors are not connected to BuildHAT ports")
            logger.error("   3. BuildHAT firmware needs update")
            logger.error("   4. Missing permissions to access /dev/ttyAMA0 (serial port)")
            return None
            
    except ImportError as e:
        logger.error(f"❌ Cannot import Motor from buildhat: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error during motor detection: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_permissions():
    """Check serial port permissions."""
    logger.info("\n" + "=" * 60)
    logger.info("Checking serial port permissions...")
    logger.info("=" * 60)
    
    import os
    
    serial_ports = ['/dev/ttyAMA0', '/dev/ttyUSB0', '/dev/ttyACM0']
    
    for port in serial_ports:
        if os.path.exists(port):
            readable = os.access(port, os.R_OK)
            writable = os.access(port, os.W_OK)
            logger.info(f"\n{port}:")
            logger.info(f"   Readable: {'✅' if readable else '❌'}")
            logger.info(f"   Writable: {'✅' if writable else '❌'}")
            
            if not (readable and writable):
                logger.warning(f"   ⚠️  Permission issue detected!")
                logger.warning(f"   Try: sudo usermod -a -G dialout $USER")
                logger.warning(f"   Then logout and login again")
        else:
            logger.debug(f"{port}: Not found")

def check_config():
    """Check configuration file."""
    logger.info("\n" + "=" * 60)
    logger.info("Checking configuration...")
    logger.info("=" * 60)
    
    try:
        from config import Config
        logger.info(f"✅ Config loaded successfully")
        logger.info(f"   Server: {Config.SERVER_HOST}:{Config.SERVER_PORT}")
        logger.info(f"   Debug: {Config.DEBUG}")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " R.O.B.E.R.T Motor Diagnostic Tool ".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # Run checks
    has_buildhat = check_buildhat_library()
    check_permissions()
    check_config()
    
    if has_buildhat:
        motors = check_motor_detection()
    else:
        motors = None
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    if has_buildhat and motors:
        logger.info("✅ Everything looks good!")
        logger.info(f"   {len(motors)} motor(s) detected")
    else:
        logger.error("❌ Issues detected:")
        if not has_buildhat:
            logger.error("   - buildhat library not installed")
        elif motors is None:
            logger.error("   - No motors detected")
        else:
            logger.error(f"   - Only {len(motors)} motor(s) detected (expected 4)")
        
        logger.error("\nNext steps:")
        logger.error("1. Check BuildHAT physical connection")
        logger.error("2. Verify motor connections to BuildHAT ports")
        logger.error("3. Run 'buildhat diagnose' (if available)")
        logger.error("4. Check Raspberry Pi logs: sudo journalctl -u buildhat")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
