# test_services/test_input_output_control.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class InputOutputControlTest:
    """Test suite for UDS Service 0x2F - Input Output Control By Identifier"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) < 4:
            return bytes([0x7F, 0x2F, 0x13])  # Incorrect message length
        
        did = int.from_bytes(request[1:3], 'big')
        control_param = request[3]
        
        if did == 0xF010:  # Valid controllable DID
            if control_param in [0x00, 0x01, 0x02, 0x03]:  # Valid control parameters
                return bytes([0x6F]) + request[1:4]  # Echo back DID and control param
            else:
                return bytes([0x7F, 0x2F, 0x31])  # Request out of range
        elif did == 0xFFFF:  # Invalid DID
            return bytes([0x7F, 0x2F, 0x31])  # Request out of range
        else:
            return bytes([0x7F, 0x2F, 0x33])  # Security access denied
    
    def test_return_control_to_ecu(self):
        """Test return control to ECU (control parameter 0x00)"""
        request = bytes([0x2F, 0xF0, 0x10, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x6F, 0xF0, 0x10, 0x00]))
        self.validator.log_test_result("Return Control to ECU", request, response, validation_result=result)
        
        self.logger.log_test(
            "Return Control to ECU",
            result['positive'] and result['valid'],
            "Control returned to ECU"
        )
    
    def test_reset_to_default(self):
        """Test reset to default (control parameter 0x01)"""
        request = bytes([0x2F, 0xF0, 0x10, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x6F, 0xF0, 0x10, 0x01]))
        self.validator.log_test_result("Reset to Default", request, response, validation_result=result)
        
        self.logger.log_test(
            "Reset to Default",
            result['positive'] and result['valid'],
            "Parameter reset to default"
        )
    
    def test_freeze_current_state(self):
        """Test freeze current state (control parameter 0x02)"""
        request = bytes([0x2F, 0xF0, 0x10, 0x02])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x6F, 0xF0, 0x10, 0x02]))
        self.validator.log_test_result("Freeze Current State", request, response, validation_result=result)
        
        self.logger.log_test(
            "Freeze Current State",
            result['positive'] and result['valid'],
            "Current state frozen"
        )
    
    def test_short_term_adjustment(self):
        """Test short term adjustment (control parameter 0x03)"""
        control_data = bytes([0x12, 0x34])  # Example control data
        request = bytes([0x2F, 0xF0, 0x10, 0x03]) + control_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x6F, 0xF0, 0x10, 0x03]))
        self.validator.log_test_result("Short Term Adjustment", request, response, validation_result=result)
        
        self.logger.log_test(
            "Short Term Adjustment",
            result['positive'] and result['valid'],
            f"Short term adjustment applied with data: {control_data.hex().upper()}"
        )
    
    def test_invalid_control_parameter(self):
        """Test invalid control parameter (0xFF)"""
        request = bytes([0x2F, 0xF0, 0x10, 0xFF])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Control Parameter", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Invalid Control Parameter",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def test_invalid_did(self):
        """Test invalid DID (0xFFFF)"""
        request = bytes([0x2F, 0xFF, 0xFF, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid DID", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Invalid DID",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all input output control tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x2F - INPUT OUTPUT CONTROL BY IDENTIFIER TESTS")
        print("="*60)
        
        self.test_return_control_to_ecu()
        self.test_reset_to_default()
        self.test_freeze_current_state()
        self.test_short_term_adjustment()
        self.test_invalid_control_parameter()
        self.test_invalid_did()
        
        self.logger.print_summary()

def main():
    test_suite = InputOutputControlTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()