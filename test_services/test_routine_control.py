# test_services/test_routine_control.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class RoutineControlTest:
    """Test suite for UDS Service 0x31 - Routine Control"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) >= 4:
            sub_func = request[1]
            routine_id = int.from_bytes(request[2:4], 'big')
            
            if routine_id == 0x0203:  # Valid routine
                if sub_func == 0x01:  # Start routine
                    return bytes([0x71, 0x01, 0x02, 0x03, 0x00])  # Success
                elif sub_func == 0x02:  # Stop routine
                    return bytes([0x71, 0x02, 0x02, 0x03, 0x00])  # Success
                elif sub_func == 0x03:  # Request results
                    return bytes([0x71, 0x03, 0x02, 0x03, 0x01, 0x23, 0x45])  # Results
            elif routine_id == 0xFFFF:  # Invalid routine
                return bytes([0x7F, 0x31, 0x31])  # Request out of range
            else:
                return bytes([0x7F, 0x31, 0x11])  # Service not supported
        
        return bytes([0x7F, 0x31, 0x13])  # Incorrect message length
    
    def test_start_routine(self):
        """Test start routine (sub-function 0x01)"""
        request = bytes([0x31, 0x01, 0x02, 0x03])  # Start routine 0x0203
        response = self.send_request(request)
        
        result = self.validator.validate_routine_control(response, 0x0203, 0x01)
        self.validator.log_test_result("Start Routine", request, response, validation_result=result)
        
        self.logger.log_test(
            "Start Routine (0x0203)",
            result['positive'] and result['valid'],
            "Routine started successfully"
        )
    
    def test_stop_routine(self):
        """Test stop routine (sub-function 0x02)"""
        request = bytes([0x31, 0x02, 0x02, 0x03])  # Stop routine 0x0203
        response = self.send_request(request)
        
        result = self.validator.validate_routine_control(response, 0x0203, 0x02)
        self.validator.log_test_result("Stop Routine", request, response, validation_result=result)
        
        self.logger.log_test(
            "Stop Routine (0x0203)",
            result['positive'] and result['valid'],
            "Routine stopped successfully"
        )
    
    def test_request_routine_results(self):
        """Test request routine results (sub-function 0x03)"""
        request = bytes([0x31, 0x03, 0x02, 0x03])  # Request results for routine 0x0203
        response = self.send_request(request)
        
        result = self.validator.validate_routine_control(response, 0x0203, 0x03)
        self.validator.log_test_result("Request Routine Results", request, response, validation_result=result)
        
        if result['positive'] and len(response) > 4:
            results_data = response[4:]
            self.logger.log_test(
                "Request Routine Results (0x0203)",
                result['valid'],
                f"Results received: {results_data.hex().upper()}"
            )
        else:
            self.logger.log_test("Request Routine Results (0x0203)", False, result['message'])
    
    def test_invalid_routine(self):
        """Test invalid routine ID (0xFFFF)"""
        request = bytes([0x31, 0x01, 0xFF, 0xFF])  # Start invalid routine
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Routine", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Invalid Routine (0xFFFF)",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def test_invalid_sub_function(self):
        """Test invalid sub-function (0x04)"""
        request = bytes([0x31, 0x04, 0x02, 0x03])  # Invalid sub-function
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Sub-Function", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Invalid Sub-Function (0x04)",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all routine control tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x31 - ROUTINE CONTROL TESTS")
        print("="*60)
        
        self.test_start_routine()
        self.test_stop_routine()
        self.test_request_routine_results()
        self.test_invalid_routine()
        self.test_invalid_sub_function()
        
        self.logger.print_summary()

def main():
    test_suite = RoutineControlTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()