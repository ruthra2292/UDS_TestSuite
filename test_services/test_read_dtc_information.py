# test_services/test_read_dtc_information.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger

class ReadDTCInformationTest:
    """Test suite for UDS Service 0x19 - Read DTC Information"""
    
    def __init__(self, connection=None):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = connection
    
    def send_request(self, request: bytes) -> bytes:
        """Send UDS request - mock implementation"""
        if len(request) < 2:
            return bytes([0x7F, 0x19, 0x13])  # Incorrect message length
        
        sub_func = request[1]
        
        if sub_func == 0x01:  # Report number of DTCs by status mask
            return bytes([0x59, 0x01, 0x00, 0x03, 0x02])  # 3 DTCs, format 0x02
        elif sub_func == 0x02:  # Report DTCs by status mask
            return bytes([0x59, 0x02, 0x00, 0x12, 0x34, 0x56, 0x08, 0x78, 0x9A, 0xBC, 0x10])
        elif sub_func == 0x06:  # Report DTCs by severity mask
            return bytes([0x59, 0x06, 0x00, 0x12, 0x34, 0x56, 0x08, 0x20])
        elif sub_func == 0x0A:  # Report supported DTCs
            return bytes([0x59, 0x0A, 0x12, 0x34, 0x56, 0x00, 0x78, 0x9A, 0xBC, 0x00])
        else:
            return bytes([0x7F, 0x19, 0x12])  # Sub-function not supported
    
    def test_report_number_of_dtcs(self):
        """Test report number of DTCs by status mask (0x01)"""
        request = bytes([0x19, 0x01, 0x00])  # All DTCs
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x59, 0x01]))
        self.validator.log_test_result("Report Number of DTCs", request, response, validation_result=result)
        
        if result['positive'] and len(response) >= 5:
            dtc_count = response[3]
            format_id = response[4]
            self.logger.log_test(
                "Report Number of DTCs",
                result['valid'],
                f"Found {dtc_count} DTCs, format: 0x{format_id:02X}"
            )
        else:
            self.logger.log_test("Report Number of DTCs", False, result['message'])
    
    def test_report_dtcs_by_status(self):
        """Test report DTCs by status mask (0x02)"""
        request = bytes([0x19, 0x02, 0x00])  # All DTCs
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x59, 0x02]))
        self.validator.log_test_result("Report DTCs by Status", request, response, validation_result=result)
        
        if result['positive'] and len(response) > 3:
            dtc_data = response[3:]
            self.logger.log_test(
                "Report DTCs by Status",
                result['valid'],
                f"DTC data: {dtc_data.hex().upper()}"
            )
        else:
            self.logger.log_test("Report DTCs by Status", False, result['message'])
    
    def test_report_dtcs_by_severity(self):
        """Test report DTCs by severity mask (0x06)"""
        request = bytes([0x19, 0x06, 0x00])  # All severities
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x59, 0x06]))
        self.validator.log_test_result("Report DTCs by Severity", request, response, validation_result=result)
        
        self.logger.log_test(
            "Report DTCs by Severity",
            result['positive'] and result['valid'],
            "DTCs reported by severity mask"
        )
    
    def test_report_supported_dtcs(self):
        """Test report supported DTCs (0x0A)"""
        request = bytes([0x19, 0x0A])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response, bytes([0x59, 0x0A]))
        self.validator.log_test_result("Report Supported DTCs", request, response, validation_result=result)
        
        self.logger.log_test(
            "Report Supported DTCs",
            result['positive'] and result['valid'],
            "Supported DTCs reported"
        )
    
    def test_unsupported_sub_function(self):
        """Test unsupported sub-function (0xFF)"""
        request = bytes([0x19, 0xFF])
        response = self.send_request(request)
        
        result = self.validator.validate_service_response(request, response)
        self.validator.log_test_result("Unsupported Sub-Function", request, response, validation_result=result)
        
        expected_negative = not result['positive'] and result.get('nrc') == 0x12
        self.logger.log_test(
            "Unsupported Sub-Function",
            expected_negative,
            f"Correctly rejected with NRC 0x12: {result['message']}"
        )
    
    def run_all_tests(self):
        """Run all read DTC information tests"""
        print("\n" + "="*60)
        print("UDS SERVICE 0x19 - READ DTC INFORMATION TESTS")
        print("="*60)
        
        self.test_report_number_of_dtcs()
        self.test_report_dtcs_by_status()
        self.test_report_dtcs_by_severity()
        self.test_report_supported_dtcs()
        self.test_unsupported_sub_function()
        
        self.logger.print_summary()

def main():
    test_suite = ReadDTCInformationTest()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()