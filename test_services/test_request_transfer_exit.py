# test_services/test_request_transfer_exit.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class RequestTransferExitTest:
    """Test suite for UDS Service 0x37 - Request Transfer Exit"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) == 1:  # No transfer request parameter record
            return bytes([0x77])  # Simple positive response
        elif len(request) > 1:  # With transfer request parameter record
            # Echo back the parameter record in response
            return bytes([0x77]) + request[1:]
        else:
            return bytes([0x7F, 0x37, 0x13])  # Incorrect message length
    
    def test_simple_transfer_exit(self):
        """Test simple transfer exit without parameters"""
        request = bytes([0x37])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x77]))
        self.validator.log_test_result("Simple Transfer Exit", request, response, validation_result=result)
        
        self.logger.log_test(
            "Simple Transfer Exit",
            result['positive'] and result['valid'],
            "Transfer session terminated successfully"
        )
    
    def test_transfer_exit_with_checksum(self):
        """Test transfer exit with checksum parameter"""
        checksum = bytes([0x12, 0x34, 0x56, 0x78])  # Example checksum
        request = bytes([0x37]) + checksum
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x77]))
        self.validator.log_test_result("Transfer Exit with Checksum", request, response, validation_result=result)
        
        if result['positive'] and len(response) > 1:
            returned_checksum = response[1:]
            self.logger.log_test(
                "Transfer Exit with Checksum",
                result['valid'] and returned_checksum == checksum,
                f"Transfer completed, checksum verified: {returned_checksum.hex().upper()}"
            )
        else:
            self.logger.log_test("Transfer Exit with Checksum", False, result['message'])
    
    def test_transfer_exit_with_signature(self):
        """Test transfer exit with signature parameter"""
        signature = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11])
        request = bytes([0x37]) + signature
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x77]))
        self.validator.log_test_result("Transfer Exit with Signature", request, response, validation_result=result)
        
        if result['positive'] and len(response) > 1:
            returned_signature = response[1:]
            self.logger.log_test(
                "Transfer Exit with Signature",
                result['valid'] and returned_signature == signature,
                f"Transfer completed, signature verified: {returned_signature.hex().upper()}"
            )
        else:
            self.logger.log_test("Transfer Exit with Signature", False, result['message'])
    
    def test_transfer_exit_with_crc(self):
        """Test transfer exit with CRC parameter"""
        crc = bytes([0xFF, 0xEE])  # Example CRC
        request = bytes([0x37]) + crc
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x77]))
        self.validator.log_test_result("Transfer Exit with CRC", request, response, validation_result=result)
        
        if result['positive'] and len(response) > 1:
            returned_crc = response[1:]
            self.logger.log_test(
                "Transfer Exit with CRC",
                result['valid'] and returned_crc == crc,
                f"Transfer completed, CRC verified: {returned_crc.hex().upper()}"
            )
        else:
            self.logger.log_test("Transfer Exit with CRC", False, result['message'])
    
    def run_all_tests(self):
        """Run all request transfer exit tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x37 - REQUEST TRANSFER EXIT TESTS")
        print("="*60)
        
        self.test_simple_transfer_exit()
        self.test_transfer_exit_with_checksum()
        self.test_transfer_exit_with_signature()
        self.test_transfer_exit_with_crc()
        
        self.logger.print_summary()

def main():
    test_suite = RequestTransferExitTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()