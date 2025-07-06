# test_services/test_transfer_data.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class TransferDataTest:
    """Test suite for UDS Service 0x36 - Transfer Data"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) < 2:
            return bytes([0x7F, 0x36, 0x13])  # Incorrect message length
        
        block_seq_counter = request[1]
        
        if block_seq_counter == 0x01:  # First block
            return bytes([0x76, 0x01])
        elif block_seq_counter == 0x02:  # Second block
            return bytes([0x76, 0x02])
        elif block_seq_counter == 0x00:  # Invalid counter
            return bytes([0x7F, 0x36, 0x73])  # Wrong block sequence counter
        else:
            return bytes([0x76, block_seq_counter])  # Echo back counter
    
    def test_first_data_block(self):
        """Test transfer first data block"""
        test_data = bytes([0xAA, 0xBB, 0xCC, 0xDD] * 16)  # 64 bytes of test data
        request = bytes([0x36, 0x01]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x76, 0x01]))
        self.validator.log_test_result("First Data Block", request, response, validation_result=result)
        
        self.logger.log_test(
            "First Data Block",
            result['positive'] and result['valid'],
            f"Transferred {len(test_data)} bytes, block sequence: 0x01"
        )
    
    def test_second_data_block(self):
        """Test transfer second data block"""
        test_data = bytes([0x11, 0x22, 0x33, 0x44] * 32)  # 128 bytes of test data
        request = bytes([0x36, 0x02]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x76, 0x02]))
        self.validator.log_test_result("Second Data Block", request, response, validation_result=result)
        
        self.logger.log_test(
            "Second Data Block",
            result['positive'] and result['valid'],
            f"Transferred {len(test_data)} bytes, block sequence: 0x02"
        )
    
    def test_wrong_sequence_counter(self):
        """Test wrong block sequence counter"""
        test_data = bytes([0xFF] * 10)
        request = bytes([0x36, 0x00]) + test_data  # Invalid counter 0x00
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Wrong Sequence Counter", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x73
        self.logger.log_test(
            "Wrong Sequence Counter",
            expected_negative,
            f"Correctly rejected with NRC 0x73: {result['message']}"
        )
    
    def test_large_data_block(self):
        """Test transfer large data block"""
        test_data = bytes(range(256)) * 4  # 1024 bytes of test data
        request = bytes([0x36, 0x03]) + test_data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x76, 0x03]))
        self.validator.log_test_result("Large Data Block", request, response, validation_result=result)
        
        self.logger.log_test(
            "Large Data Block",
            result['positive'] and result['valid'],
            f"Transferred {len(test_data)} bytes, block sequence: 0x03"
        )
    
    def test_empty_data_block(self):
        """Test transfer empty data block"""
        request = bytes([0x36, 0x04])  # No data
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x76, 0x04]))
        self.validator.log_test_result("Empty Data Block", request, response, validation_result=result)
        
        self.logger.log_test(
            "Empty Data Block",
            result['positive'] and result['valid'],
            "Empty data block accepted"
        )
    
    def test_invalid_length(self):
        """Test invalid message length"""
        request = bytes([0x36])  # Missing block sequence counter
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid Length", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x13
        self.logger.log_test(
            "Invalid Length",
            expected_negative,
            f"Correctly rejected with NRC 0x13: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all transfer data tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x36 - TRANSFER DATA TESTS")
        print("="*60)
        
        self.test_first_data_block()
        self.test_second_data_block()
        self.test_wrong_sequence_counter()
        self.test_large_data_block()
        self.test_empty_data_block()
        self.test_invalid_length()
        
        self.logger.print_summary()

def main():
    test_suite = TransferDataTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()