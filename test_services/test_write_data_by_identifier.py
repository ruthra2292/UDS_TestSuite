# test_services/test_write_data_by_identifier.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class WriteDataByIdentifierTest:
    """Test suite for UDS Service 0x2E - Write Data By Identifier"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) >= 3 and request[:2] == bytes([0x2E, 0xF1]):
            if request[2] == 0x90:  # VIN - read only
                return bytes([0x7F, 0x2E, 0x33])  # Security access denied
            elif request[2] == 0x10:  # Writable DID
                return bytes([0x6E, 0xF1, 0x10])  # Positive response
            elif request[2] == 0xFF:  # Invalid DID
                return bytes([0x7F, 0x2E, 0x31])  # Request out of range
        return bytes([0x7F, 0x2E, 0x13])  # Incorrect message length
    
    def test_write_valid_did(self):
        """Test writing to valid writable DID (0xF110)"""
        test_data = b"TEST_DATA_123"
        request = bytes([0x2E, 0xF1, 0x10]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_write_data_by_identifier(response, 0xF110)
        self.validator.log_test_result("Write Valid DID", request, response, validation_result=result)
        
        self.logger.log_test(
            "Write Valid DID (0xF110)",
            result['positive'] and result['valid'],
            f"Successfully wrote {len(test_data)} bytes"
        )
    
    def test_write_readonly_did(self):
        """Test writing to read-only DID (0xF190 - VIN)"""
        test_data = b"1HGBH41JXMN109186"
        request = bytes([0x2E, 0xF1, 0x90]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Write Read-Only DID", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x33
        self.logger.log_test(
            "Write Read-Only DID (0xF190)",
            expected_negative,
            f"Correctly rejected with NRC 0x33: {result['message']}"
        )
    
    def test_write_invalid_did(self):
        """Test writing to invalid DID (0xF1FF)"""
        test_data = b"INVALID"
        request = bytes([0x2E, 0xF1, 0xFF]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Write Invalid DID", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Write Invalid DID (0xF1FF)",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def test_write_empty_data(self):
        """Test writing empty data"""
        request = bytes([0x2E, 0xF1, 0x10])  # No data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Write Empty Data", request, response, validation_result=result)
        
        # Should still work for some DIDs
        self.logger.log_test(
            "Write Empty Data",
            result['positive'],
            "Empty data write handled"
        )
    
    def run_all_tests(self):
        """Run all write data by identifier tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x2E - WRITE DATA BY IDENTIFIER TESTS")
        print("="*60)
        
        self.test_write_valid_did()
        self.test_write_readonly_did()
        self.test_write_invalid_did()
        self.test_write_empty_data()
        
        self.logger.print_summary()

def main():
    test_suite = WriteDataByIdentifierTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()