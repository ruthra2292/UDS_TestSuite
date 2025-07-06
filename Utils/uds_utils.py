# utils/uds_utils.py
import time
from typing import Dict, List, Optional

# Complete NRC dictionary from ISO 14229
NRC_DESCRIPTIONS = {
    0x10: "General reject",
    0x11: "Service not supported",
    0x12: "Sub-function not supported",
    0x13: "Incorrect message length or invalid format",
    0x14: "Response too long",
    0x21: "Busy repeat request",
    0x22: "Conditions not correct",
    0x24: "Request sequence error",
    0x25: "No response from subnet component",
    0x26: "Failure prevents execution of requested action",
    0x31: "Request out of range",
    0x33: "Security access denied",
    0x35: "Invalid key",
    0x36: "Exceed number of attempts",
    0x37: "Required time delay not expired",
    0x70: "Upload download not accepted",
    0x71: "Transfer data suspended",
    0x72: "General programming failure",
    0x73: "Wrong block sequence counter",
    0x78: "Request correctly received - response pending",
    0x7E: "Sub-function not supported in active session",
    0x7F: "Service not supported in active session",
    0x81: "RPM too high",
    0x82: "RPM too low",
    0x83: "Engine is running",
    0x84: "Engine is not running",
    0x85: "Engine run time too low",
    0x86: "Temperature too high",
    0x87: "Temperature too low",
    0x88: "Vehicle speed too high",
    0x89: "Vehicle speed too low",
    0x8A: "Throttle/pedal too high",
    0x8B: "Throttle/pedal too low",
    0x8C: "Transmission range not in neutral",
    0x8D: "Transmission range not in gear",
    0x8F: "Brake switch(es) not closed",
    0x90: "Shifter lever not in park",
    0x91: "Torque converter clutch locked",
    0x92: "Voltage too high",
    0x93: "Voltage too low"
}

def decode_nrc(nrc_byte: int) -> str:
    """Decode NRC byte to human-readable description"""
    return NRC_DESCRIPTIONS.get(nrc_byte, f"Unknown NRC (0x{nrc_byte:02X})")

def format_hex_data(data: bytes, separator: str = " ") -> str:
    """Format bytes as hex string with separator"""
    return separator.join(f"{b:02X}" for b in data)

def parse_hex_string(hex_str: str) -> bytes:
    """Parse hex string to bytes"""
    hex_str = hex_str.replace(" ", "").replace("0x", "")
    return bytes.fromhex(hex_str)

def retry_on_pending(func, max_retries: int = 5, delay: float = 0.1):
    """Decorator to handle 0x78 response pending"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                response = func(*args, **kwargs)
                if response and len(response) >= 3 and response[0] == 0x7F and response[2] == 0x78:
                    time.sleep(delay)
                    continue
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
        return None
    return wrapper

class TestLogger:
    """Simple test result logger"""
    
    def __init__(self):
        self.results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': time.time()
        }
        self.results.append(result)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {details}")
    
    def get_summary(self) -> Dict:
        """Get test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }
    
    def print_summary(self):
        """Print test summary"""
        summary = self.get_summary()
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"{'='*50}")