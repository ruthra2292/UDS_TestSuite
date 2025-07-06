# test_services/test_ecu_reset.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class ECUResetTest:
    """Test suite for UDS Service 0x11 - ECU Reset"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if request == bytes([0x11, 0x01]):  # Hard reset
            return bytes([0x51, 0x01])
        elif request == bytes([0x11, 0x02]):  # Key off on reset
            return bytes([0x51, 0x02])
        elif request == bytes([0x11, 0x03]):  # Soft reset
            return bytes([0x51, 0x03])
        elif request == bytes([0x11, 0x04]):  # Enable rapid power shutdown
            return bytes([0x7F, 0x11, 0x12])  # Sub-function not supported
        else:
            return bytes([0x7F, 0x11, 0x13])  # Incorrect message length
    
    def test_hard_reset(self):
        """Test hard reset (0x01)"""
        request = bytes([0x11, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_ecu_reset(response, 0x01)
        self.validator.log_test_result("Hard Reset", request, response, validation_result=result)
        
        self.logger.log_test(
            "Hard Reset (0x01)",
            result['positive'] and result['valid'],
            "ECU hard reset acknowledged"
        )
    
    def test_key_off_on_reset(self):
        """Test key off on reset (0x02)"""
        request = bytes([0x11, 0x02])
        response = self.send_request(request)
        
        result = self.validator.validate_ecu_reset(response, 0x02)
        self.validator.log_test_result("Key Off On Reset", request, response, validation_result=result)
        
        self.logger.log_test(
            "Key Off On Reset (0x02)",
            result['positive'] and result['valid'],
            "ECU key off on reset acknowledged"
        )
    
    def test_soft_reset(self):
        """Test soft reset (0x03)"""
        request = bytes([0x11, 0x03])
        response = self.send_request(request)
        
        result = self.validator.validate_ecu_reset(response, 0x03)
        self.validator.log_test_result("Soft Reset", request, response, validation_result=result)
        
        self.logger.log_test(
            "Soft Reset (0x03)",
            result['positive'] and result['valid'],
            "ECU soft reset acknowledged"
        )
    
    def test_unsupported_reset(self):
        """Test unsupported reset type (0x04)"""
        request = bytes([0x11, 0x04])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Unsupported Reset", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Unsupported Reset (0x04)",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all ECU reset tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x11 - ECU RESET TESTS")
        print("="*60)
        
        self.test_hard_reset()
        self.test_key_off_on_reset()
        self.test_soft_reset()
        self.test_unsupported_reset()
        
        self.logger.print_summary()

def main():
    test_suite = ECUResetTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()