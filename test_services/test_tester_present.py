# test_services/test_tester_present.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class TesterPresentTest:
    """Test suite for UDS Service 0x3E - Tester Present"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if request == bytes([0x3E, 0x00]):  # Zero sub-function
            return bytes([0x7E, 0x00])
        elif request == bytes([0x3E, 0x80]):  # Suppress positive response
            return bytes()  # No response expected
        elif len(request) == 2 and request[0] == 0x3E:
            return bytes([0x7F, 0x3E, 0x12])  # Sub-function not supported
        else:
            return bytes([0x7F, 0x3E, 0x13])  # Incorrect message length
    
    def test_tester_present_normal(self):
        """Test normal tester present (sub-function 0x00)"""
        request = bytes([0x3E, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_tester_present(response, 0x00)
        self.validator.log_test_result("Tester Present Normal", request, response, validation_result=result)
        
        self.logger.log_test(
            "Tester Present (0x00)",
            result['positive'] and result['valid'],
            "Tester present acknowledged"
        )
    
    def test_tester_present_suppress_response(self):
        """Test tester present with suppress positive response (sub-function 0x80)"""
        request = bytes([0x3E, 0x80])
        response = self.send_request(request)
        
        # For suppress positive response, we expect no response
        if len(response) == 0:
            self.logger.log_test(
                "Tester Present Suppress (0x80)",
                True,
                "No response received as expected (suppress positive response)"
            )
        else:
            # If we get a response, validate it
            result = self.validator.validate_service_response(request, response)
            self.validator.log_test_result("Tester Present Suppress", request, response, validation_result=result)
            
            self.logger.log_test(
                "Tester Present Suppress (0x80)",
                not result['positive'],  # Should be negative or no response
                f"Unexpected response: {result['message']}"
            )
    
    def test_invalid_sub_function(self):
        """Test invalid sub-function (0x01)"""
        request = bytes([0x3E, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Sub-Function", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Invalid Sub-Function (0x01)",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def test_invalid_length(self):
        """Test invalid message length"""
        request = bytes([0x3E])  # Missing sub-function
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Length", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x13
        self.logger.log_test(
            "Invalid Message Length",
            expected_negative,
            f"Correctly rejected with NRC 0x13: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all tester present tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x3E - TESTER PRESENT TESTS")
        print("="*60)
        
        self.test_tester_present_normal()
        self.test_tester_present_suppress_response()
        self.test_invalid_sub_function()
        self.test_invalid_length()
        
        self.logger.print_summary()

def main():
    test_suite = TesterPresentTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()