# test_services/test_read_data_by_identifier.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class ReadDataByIdentifierTest:
    """Test suite for UDS Service 0x22 - Read Data By Identifier"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if request == bytes([0x22, 0xF1, 0x90]):  # VIN
            return bytes([0x62, 0xF1, 0x90]) + b"1HGBH41JXMN109186"
        elif request == bytes([0x22, 0xF1, 0x86]):  # Active diagnostic session
            return bytes([0x62, 0xF1, 0x86, 0x01])  # Default session
        elif request == bytes([0x22, 0xF1, 0x87]):  # Vehicle manufacturer spare part number
            return bytes([0x62, 0xF1, 0x87]) + b"37820-RBB-003"
        elif request == bytes([0x22, 0xF1, 0x88]):  # Vehicle manufacturer ECU software number
            return bytes([0x62, 0xF1, 0x88]) + b"39990-TBA-A030"
        elif request == bytes([0x22, 0xFF, 0xFF]):  # Invalid DID
            return bytes([0x7F, 0x22, 0x31])  # Request out of range
        else:
            return bytes([0x7F, 0x22, 0x13])  # Incorrect message length
    
    def test_read_vin(self):
        """Test reading VIN (DID 0xF190)"""
        request = bytes([0x22, 0xF1, 0x90])
        response = self.send_request(request)
        
        result = self.validator.validate_read_data_by_identifier(response, 0xF190)
        self.validator.log_test_result("Read VIN", request, response, validation_result=result)
        
        if result['positive'] and 'data' in result:
            vin = result['data'].decode('ascii', errors='ignore')
            self.logger.log_test(
                "Read VIN (0xF190)",
                result['valid'],
                f"VIN: {vin}"
            )
        else:
            self.logger.log_test("Read VIN (0xF190)", False, result['message'])
    
    def test_read_active_session(self):
        """Test reading active diagnostic session (DID 0xF186)"""
        request = bytes([0x22, 0xF1, 0x86])
        response = self.send_request(request)
        
        result = self.validator.validate_read_data_by_identifier(response, 0xF186)
        self.validator.log_test_result("Read Active Session", request, response, validation_result=result)
        
        if result['positive'] and 'data' in result:
            session = result['data'][0] if result['data'] else 0
            session_names = {1: "Default", 2: "Programming", 3: "Extended"}
            self.logger.log_test(
                "Read Active Session (0xF186)",
                result['valid'],
                f"Active session: {session_names.get(session, f'Unknown (0x{session:02X})')}"
            )
        else:
            self.logger.log_test("Read Active Session (0xF186)", False, result['message'])
    
    def test_read_spare_part_number(self):
        """Test reading spare part number (DID 0xF187)"""
        request = bytes([0x22, 0xF1, 0x87])
        response = self.send_request(request)
        
        result = self.validator.validate_read_data_by_identifier(response, 0xF187)
        self.validator.log_test_result("Read Spare Part Number", request, response, validation_result=result)
        
        if result['positive'] and 'data' in result:
            part_number = result['data'].decode('ascii', errors='ignore')
            self.logger.log_test(
                "Read Spare Part Number (0xF187)",
                result['valid'],
                f"Part Number: {part_number}"
            )
        else:
            self.logger.log_test("Read Spare Part Number (0xF187)", False, result['message'])
    
    def test_read_software_number(self):
        """Test reading software number (DID 0xF188)"""
        request = bytes([0x22, 0xF1, 0x88])
        response = self.send_request(request)
        
        result = self.validator.validate_read_data_by_identifier(response, 0xF188)
        self.validator.log_test_result("Read Software Number", request, response, validation_result=result)
        
        if result['positive'] and 'data' in result:
            software_number = result['data'].decode('ascii', errors='ignore')
            self.logger.log_test(
                "Read Software Number (0xF188)",
                result['valid'],
                f"Software Number: {software_number}"
            )
        else:
            self.logger.log_test("Read Software Number (0xF188)", False, result['message'])
    
    def test_invalid_did(self):
        """Test reading invalid DID (0xFFFF)"""
        request = bytes([0x22, 0xFF, 0xFF])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Invalid DID", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x31
        self.logger.log_test(
            "Invalid DID (0xFFFF)",
            expected_negative,
            f"Correctly rejected with NRC 0x31: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all read data by identifier tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x22 - READ DATA BY IDENTIFIER TESTS")
        print("="*60)
        
        self.test_read_vin()
        self.test_read_active_session()
        self.test_read_spare_part_number()
        self.test_read_software_number()
        self.test_invalid_did()
        
        self.logger.print_summary()

def main():
    test_suite = ReadDataByIdentifierTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()