# test_services/test_clear_diagnostic_information.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class ClearDiagnosticInformationTest:
    """Test suite for UDS Service 0x14 - Clear Diagnostic Information"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if request == bytes([0x14, 0xFF, 0xFF, 0xFF]):  # Clear all DTCs
            return bytes([0x54])
        elif request == bytes([0x14, 0x00, 0x00, 0x00]):  # Clear powertrain DTCs
            return bytes([0x54])
        elif len(request) != 4:
            return bytes([0x7F, 0x14, 0x13])  # Incorrect message length
        else:
            return bytes([0x54])  # Success for other group masks
    
    def test_clear_all_dtcs(self):
        """Test clear all DTCs (0xFFFFFF)"""
        request = bytes([0x14, 0xFF, 0xFF, 0xFF])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x54]))
        self.validator.log_test_result("Clear All DTCs", request, response, validation_result=result)
        
        self.logger.log_test(
            "Clear All DTCs",
            result['positive'] and result['valid'],
            "All diagnostic trouble codes cleared"
        )
    
    def test_clear_powertrain_dtcs(self):
        """Test clear powertrain DTCs (0x000000)"""
        request = bytes([0x14, 0x00, 0x00, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x54]))
        self.validator.log_test_result("Clear Powertrain DTCs", request, response, validation_result=result)
        
        self.logger.log_test(
            "Clear Powertrain DTCs",
            result['positive'] and result['valid'],
            "Powertrain DTCs cleared"
        )
    
    def test_invalid_length(self):
        """Test invalid message length"""
        request = bytes([0x14, 0xFF, 0xFF])  # Missing byte
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
        """Run all clear diagnostic information tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x14 - CLEAR DIAGNOSTIC INFORMATION TESTS")
        print("="*60)
        
        self.test_clear_all_dtcs()
        self.test_clear_powertrain_dtcs()
        self.test_invalid_length()
        
        self.logger.print_summary()

def main():
    test_suite = ClearDiagnosticInformationTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()