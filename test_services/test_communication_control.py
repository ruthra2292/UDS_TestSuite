# test_services/test_communication_control.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class CommunicationControlTest:
    """Test suite for UDS Service 0x28 - Communication Control"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) < 2:
            return bytes([0x7F, 0x28, 0x13])  # Incorrect message length
        
        control_type = request[1]
        
        if control_type == 0x00:  # Enable Rx and Tx
            return bytes([0x68, 0x00])
        elif control_type == 0x01:  # Enable Rx, disable Tx
            return bytes([0x68, 0x01])
        elif control_type == 0x02:  # Disable Rx, enable Tx
            return bytes([0x68, 0x02])
        elif control_type == 0x03:  # Disable Rx and Tx
            return bytes([0x68, 0x03])
        else:
            return bytes([0x7F, 0x28, 0x12])  # Sub-function not supported
    
    def test_enable_rx_tx(self):
        """Test enable Rx and Tx (0x00)"""
        request = bytes([0x28, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x68, 0x00]))
        self.validator.log_test_result("Enable Rx and Tx", request, response, validation_result=result)
        
        self.logger.log_test(
            "Enable Rx and Tx",
            result['positive'] and result['valid'],
            "Normal communication enabled"
        )
    
    def test_enable_rx_disable_tx(self):
        """Test enable Rx, disable Tx (0x01)"""
        request = bytes([0x28, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x68, 0x01]))
        self.validator.log_test_result("Enable Rx, Disable Tx", request, response, validation_result=result)
        
        self.logger.log_test(
            "Enable Rx, Disable Tx",
            result['positive'] and result['valid'],
            "Receive enabled, transmit disabled"
        )
    
    def test_disable_rx_enable_tx(self):
        """Test disable Rx, enable Tx (0x02)"""
        request = bytes([0x28, 0x02])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x68, 0x02]))
        self.validator.log_test_result("Disable Rx, Enable Tx", request, response, validation_result=result)
        
        self.logger.log_test(
            "Disable Rx, Enable Tx",
            result['positive'] and result['valid'],
            "Receive disabled, transmit enabled"
        )
    
    def test_disable_rx_tx(self):
        """Test disable Rx and Tx (0x03)"""
        request = bytes([0x28, 0x03])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x68, 0x03]))
        self.validator.log_test_result("Disable Rx and Tx", request, response, validation_result=result)
        
        self.logger.log_test(
            "Disable Rx and Tx",
            result['positive'] and result['valid'],
            "All communication disabled"
        )
    
    def test_invalid_control_type(self):
        """Test invalid control type (0xFF)"""
        request = bytes([0x28, 0xFF])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Control Type", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Invalid Control Type",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all communication control tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x28 - COMMUNICATION CONTROL TESTS")
        print("="*60)
        
        self.test_enable_rx_tx()
        self.test_enable_rx_disable_tx()
        self.test_disable_rx_enable_tx()
        self.test_disable_rx_tx()
        self.test_invalid_control_type()
        
        self.logger.print_summary()

def main():
    test_suite = CommunicationControlTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()