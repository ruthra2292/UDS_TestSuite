# test_services/test_diagnostic_session_control.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger, retry_on_pending

class DiagnosticSessionControlTest:
    """Test suite for UDS Service 0x10 - Diagnostic Session Control"""
    
    def __init__(self, connection=None, transport_type="mock"):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
        self.transport_type = transport_type
        
        # Initialize transport handlers
        if transport_type == "doip":
            from Utils.doip_handler import DoIPHandler
            self.doip_handler = DoIPHandler("192.168.1.100")
        elif transport_type == "dosoad":
            from Utils.doip_handler import DoSOADHandler
            self.dosoad_handler = DoSOADHandler()
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request via configured transport"""
        if self.transport_type == "doip" and hasattr(self, 'doip_handler'):
            if self.doip_handler.connect():
                response = self.doip_handler.send_diagnostic_message(request)
                self.doip_handler.disconnect()
                return response if response else bytes([0x7F, request[0], 0x25])
        elif self.transport_type == "dosoad" and hasattr(self, 'dosoad_handler'):
            soad_request = self.dosoad_handler.create_soad_request(request)
            # Mock DoSOAD response
            soad_response = self._mock_dosoad_response(soad_request)
            return self.dosoad_handler.parse_soad_response(soad_response)
        
        # Default mock responses
        if request == bytes([0x10, 0x01]):
            return bytes([0x50, 0x01, 0x00, 0x32, 0x01, 0xF4])
        elif request == bytes([0x10, 0x02]):
            return bytes([0x50, 0x02, 0x00, 0x32, 0x01, 0xF4])
        elif request == bytes([0x10, 0x03]):
            return bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])
        elif request == bytes([0x10, 0x04]):
            return bytes([0x7F, 0x10, 0x12])
        else:
            return bytes([0x7F, 0x10, 0x13])
    
    def _mock_dosoad_response(self, soad_request: bytes) -> bytes:
        """Mock DoSOAD response"""
        if len(soad_request) > 16:
            uds_request = soad_request[16:]
            uds_response = self.send_request(uds_request) if hasattr(self, '_in_mock') else bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])
            return bytes([0x12, 0x34, 0x80, 0x01, 0x00, len(uds_response) + 8, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00]) + uds_response
        return bytes()
    
    def test_default_session(self):
        """Test default diagnostic session (0x01)"""
        request = bytes([0x10, 0x01])
        response = self.send_request(request)
        
        result = self.validator.validate_diagnostic_session_control(response, 0x01)
        self.validator.log_test_result("Default Session Control", request, response, validation_result=result)
        
        self.logger.log_test(
            "Default Session (0x01)",
            result['positive'] and result['valid'],
            f"Session changed to default, timing: {result.get('timing', 'N/A')}"
        )
    
    def test_programming_session(self):
        """Test programming diagnostic session (0x02)"""
        request = bytes([0x10, 0x02])
        response = self.send_request(request)
        
        result = self.validator.validate_diagnostic_session_control(response, 0x02)
        self.validator.log_test_result("Programming Session Control", request, response, validation_result=result)
        
        self.logger.log_test(
            "Programming Session (0x02)",
            result['positive'] and result['valid'],
            f"Session changed to programming, timing: {result.get('timing', 'N/A')}"
        )
    
    def test_extended_session(self):
        """Test extended diagnostic session (0x03)"""
        request = bytes([0x10, 0x03])
        response = self.send_request(request)
        
        result = self.validator.validate_diagnostic_session_control(response, 0x03)
        self.validator.log_test_result("Extended Session Control", request, response, validation_result=result)
        
        self.logger.log_test(
            "Extended Session (0x03)",
            result['positive'] and result['valid'],
            f"Session changed to extended, timing: {result.get('timing', 'N/A')}"
        )
    
    def test_unsupported_session(self):
        """Test unsupported diagnostic session (0x04)"""
        request = bytes([0x10, 0x04])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Unsupported Session Control", request, response, validation_result=result)
        
        # Expect negative response
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Unsupported Session (0x04)",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all diagnostic session control tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x10 - DIAGNOSTIC SESSION CONTROL TESTS")
        print("="*60)
        
        self.test_default_session()
        self.test_programming_session()
        self.test_extended_session()
        self.test_unsupported_session()
        
        self.logger.print_summary()

def main():
    """Main test execution"""
    test_suite = DiagnosticSessionControlTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()