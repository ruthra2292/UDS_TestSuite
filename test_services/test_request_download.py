# test_services/test_request_download.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class RequestDownloadTest:
    """Test suite for UDS Service 0x34 - Request Download"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) < 3:
            return bytes([0x7F, 0x34, 0x13])  # Incorrect message length
        
        data_format = request[1]
        addr_len_format = request[2]
        
        if data_format == 0x00 and addr_len_format == 0x44:  # Valid format
            # Mock response with max block length
            return bytes([0x74, 0x20, 0x10, 0x00])  # Max 4096 bytes per block
        elif data_format == 0xFF:  # Invalid format
            return bytes([0x7F, 0x34, 0x31])  # Request out of range
        else:
            return bytes([0x7F, 0x34, 0x22])  # Conditions not correct
    
    def test_valid_download_request(self):
        """Test valid download request"""
        # Format: dataFormatIdentifier=0x00, addressAndLengthFormatIdentifier=0x44
        # memoryAddress=0x12345678 (4 bytes), memorySize=0x1000 (4 bytes)
        request = bytes([0x34, 0x00, 0x44, 0x12, 0x34, 0x56, 0x78, 0x00, 0x00, 0x10, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x74]))
        self.validator.log_test_result("Valid Download Request", request, response, validation_result=result)
        
        if result['positive'] and len(response) >= 4:
            length_format = response[1]
            max_block_length = int.from_bytes(response[2:], 'big')
            self.logger.log_test(
                "Valid Download Request",
                result['valid'],
                f"Download accepted, max block length: {max_block_length} bytes"
            )
        else:
            self.logger.log_test("Valid Download Request", False, result['message'])
    
    def test_invalid_data_format(self):
        """Test invalid data format identifier"""
        request = bytes([0x34, 0xFF, 0x44, 0x12, 0x34, 0x56, 0x78, 0x00, 0x00, 0x10, 0x00])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Data Format", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Invalid Data Format",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def test_invalid_address_format(self):
        """Test invalid address and length format"""
        request = bytes([0x34, 0x00, 0xFF, 0x12, 0x34, 0x56, 0x78])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Address Format", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x22
        self.logger.log_test(
            "Invalid Address Format",
            expected_negative,
            f"Correctly rejected with NRC 0x22: {result['message']}"
        )
    
    def test_insufficient_length(self):
        """Test insufficient message length"""
        request = bytes([0x34, 0x00])  # Missing required parameters
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Insufficient Length", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x13
        self.logger.log_test(
            "Insufficient Length",
            expected_negative,
            f"Correctly rejected with NRC 0x13: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all request download tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x34 - REQUEST DOWNLOAD TESTS")
        print("="*60)
        
        self.test_valid_download_request()
        self.test_invalid_data_format()
        self.test_invalid_address_format()
        self.test_insufficient_length()
        
        self.logger.print_summary()

def main():
    test_suite = RequestDownloadTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()