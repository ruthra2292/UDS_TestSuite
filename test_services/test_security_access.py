# test_services/test_security_access.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class SecurityAccessTest:
    """Test suite for UDS Service 0x27 - Security Access"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) >= 2:
            sub_func = request[1]
            
            if sub_func == 0x01:  # Request seed for level 1
                return bytes([0x67, 0x01, 0x12, 0x34, 0x56, 0x78])  # Seed
            elif sub_func == 0x02:  # Send key for level 1
                if len(request) >= 6:
                    # Simple key validation (seed XOR 0xFF)
                    expected_key = bytes([0xED, 0xCB, 0xA9, 0x87])
                    if request[2:6] == expected_key:
                        return bytes([0x67, 0x02])  # Access granted
                    else:
                        return bytes([0x7F, 0x27, 0x35])  # Invalid key
                else:
                    return bytes([0x7F, 0x27, 0x13])  # Incorrect message length
            elif sub_func == 0x03:  # Request seed for level 2
                return bytes([0x67, 0x03, 0xAB, 0xCD, 0xEF, 0x01])  # Seed
            elif sub_func == 0x04:  # Send key for level 2
                return bytes([0x7F, 0x27, 0x35])  # Invalid key (for testing)
            else:
                return bytes([0x7F, 0x27, 0x12])  # Sub-function not supported
        
        return bytes([0x7F, 0x27, 0x13])  # Incorrect message length
    
    def test_request_seed_level1(self):
        """Test request seed for security level 1"""
        request = bytes([0x27, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_security_access(response, 0x01)
        self.validator.log_test_result("Request Seed Level 1", request, response, validation_result=result)
        
        if result['positive'] and 'seed' in result:
            seed_hex = result['seed'].hex().upper()
            self.logger.log_test(
                "Request Seed Level 1",
                result['valid'],
                f"Seed received: {seed_hex}"
            )
        else:
            self.logger.log_test("Request Seed Level 1", False, result['message'])
    
    def test_send_valid_key_level1(self):
        """Test sending valid key for security level 1"""
        # First get seed
        seed_request = bytes([0x27, 0x01])
        seed_response = self.send_request(seed_request)
        
        # Calculate key (simple XOR for demo)
        key = bytes([0xED, 0xCB, 0xA9, 0x87])
        key_request = bytes([0x27, 0x02]) + key
        key_response = self.send_request(key_request)
        
        result = self.validator.validate_security_access(key_response, 0x02)
        self.validator.log_test_result("Send Valid Key Level 1", key_request, key_response, validation_result=result)
        
        self.logger.log_test(
            "Send Valid Key Level 1",
            result['positive'] and result['valid'],
            "Security access granted"
        )
    
    def test_send_invalid_key_level1(self):
        """Test sending invalid key for security level 1"""
        invalid_key = bytes([0x00, 0x00, 0x00, 0x00])
        request = bytes([0x27, 0x02]) + invalid_key
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Send Invalid Key Level 1", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x35
        self.logger.log_test(
            "Send Invalid Key Level 1",
            expected_negative,
            f"Correctly rejected with NRC 0x35: {result['message']}"
        )
    
    def test_request_seed_level2(self):
        """Test request seed for security level 2"""
        request = bytes([0x27, 0x03])
        response = self.send_request(request)
        
        result = self.validator.validate_security_access(response, 0x03)
        self.validator.log_test_result("Request Seed Level 2", request, response, validation_result=result)
        
        if result['positive'] and 'seed' in result:
            seed_hex = result['seed'].hex().upper()
            self.logger.log_test(
                "Request Seed Level 2",
                result['valid'],
                f"Seed received: {seed_hex}"
            )
        else:
            self.logger.log_test("Request Seed Level 2", False, result['message'])
    
    def test_invalid_sub_function(self):
        """Test invalid sub-function (0x05)"""
        request = bytes([0x27, 0x05])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Sub-Function", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Invalid Sub-Function (0x05)",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all security access tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x27 - SECURITY ACCESS TESTS")
        print("="*60)
        
        self.test_request_seed_level1()
        self.test_send_valid_key_level1()
        self.test_send_invalid_key_level1()
        self.test_request_seed_level2()
        self.test_invalid_sub_function()
        
        self.logger.print_summary()

def main():
    test_suite = SecurityAccessTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()