# uds_validator_extended.py
import logging
import time
from typing import Optional, Tuple, Dict, List

# Complete NRC dictionary based on ISO 14229
NRC_DICT = {
    0x10: "General reject",
    0x11: "Service not supported",
    0x12: "Sub-function not supported",
    0x13: "Incorrect message length or invalid format",
    0x14: "Response too long",
    0x21: "Busy repeat request",
    0x22: "Conditions not correct",
    0x24: "Request sequence error",
    0x25: "No response from subnet component",
    0x26: "Failure prevents execution of requested action",
    0x31: "Request out of range",
    0x33: "Security access denied",
    0x35: "Invalid key",
    0x36: "Exceed number of attempts",
    0x37: "Required time delay not expired",
    0x70: "Upload download not accepted",
    0x71: "Transfer data suspended",
    0x72: "General programming failure",
    0x73: "Wrong block sequence counter",
    0x78: "Request correctly received - response pending",
    0x7E: "Sub-function not supported in active session",
    0x7F: "Service not supported in active session",
    0x81: "RPM too high",
    0x82: "RPM too low",
    0x83: "Engine is running",
    0x84: "Engine is not running",
    0x85: "Engine run time too low",
    0x86: "Temperature too high",
    0x87: "Temperature too low",
    0x88: "Vehicle speed too high",
    0x89: "Vehicle speed too low",
    0x8A: "Throttle/pedal too high",
    0x8B: "Throttle/pedal too low",
    0x8C: "Transmission range not in neutral",
    0x8D: "Transmission range not in gear",
    0x8F: "Brake switch(es) not closed",
    0x90: "Shifter lever not in park",
    0x91: "Torque converter clutch locked",
    0x92: "Voltage too high",
    0x93: "Voltage too low"
}

class UDSValidator:
    """Extended UDS validation class for ISO 14229 compliance testing"""
    
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def is_positive_response(self, response: bytes) -> bool:
        """Check if response is positive (not 0x7F)"""
        return response and len(response) > 0 and response[0] != 0x7F
    
    def parse_response(self, response: bytes) -> Tuple[str, bool]:
        """Parse UDS response and return interpretation with status"""
        if not response or len(response) == 0:
            return "Empty response", False
        
        if self.is_positive_response(response):
            service_id = response[0] - 0x40
            return f"Positive response for SID 0x{service_id:02X}", True
        elif response[0] == 0x7F and len(response) >= 3:
            requested_sid = response[1]
            nrc = response[2]
            nrc_desc = NRC_DICT.get(nrc, 'Unknown NRC')
            return f"Negative response for SID 0x{requested_sid:02X} -> NRC 0x{nrc:02X}: {nrc_desc}", False
        else:
            return "Invalid response format", False
    
    def validate_response_format(self, response: bytes, expected_min_length: int = 1) -> bool:
        """Validate basic response format"""
        return response and len(response) >= expected_min_length
    
    def validate_service_response(self, request: bytes, response: bytes, expected_prefix: bytes = None) -> Dict:
        """Comprehensive service response validation"""
        result = {
            'valid': False,
            'positive': False,
            'message': '',
            'nrc': None,
            'service_id': None
        }
        
        if not self.validate_response_format(response):
            result['message'] = "Invalid response format"
            return result
        
        parsed_msg, is_positive = self.parse_response(response)
        result['message'] = parsed_msg
        result['positive'] = is_positive
        
        if is_positive:
            result['service_id'] = response[0] - 0x40
            if expected_prefix and response.startswith(expected_prefix):
                result['valid'] = True
            elif not expected_prefix:
                result['valid'] = True
        else:
            if len(response) >= 3:
                result['nrc'] = response[2]
        
        return result
    
    def log_test_result(self, test_name: str, request: bytes, response: bytes, 
                       expected: bytes = None, validation_result: Dict = None):
        """Log comprehensive test results"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"Test: {test_name}")
        self.logger.info(f"Request:  {request.hex().upper()}")
        self.logger.info(f"Response: {response.hex().upper()}")
        
        if validation_result:
            self.logger.info(f"Result: {validation_result['message']}")
            if validation_result['positive']:
                status = "[PASS]" if validation_result['valid'] else "[FAIL]"
                self.logger.info(f"Status: {status}")
            else:
                self.logger.warning(f"Status: [NEGATIVE] (NRC: 0x{validation_result.get('nrc', 0):02X})")
        
        if expected:
            self.logger.info(f"Expected: {expected.hex().upper()}")
        
        self.logger.info(f"{'='*50}")
    
    # Service-specific validation methods
    def validate_diagnostic_session_control(self, response: bytes, expected_session: int) -> Dict:
        """Validate 0x10 Diagnostic Session Control response"""
        result = self.validate_service_response(None, response, bytes([0x50, expected_session]))
        if result['positive'] and len(response) >= 6:
            p2_server_max = int.from_bytes(response[2:4], 'big')
            p2_star_server_max = int.from_bytes(response[4:6], 'big')
            result['timing'] = {'p2_max': p2_server_max, 'p2_star_max': p2_star_server_max}
        return result
    
    def validate_ecu_reset(self, response: bytes, reset_type: int) -> Dict:
        """Validate 0x11 ECU Reset response"""
        return self.validate_service_response(None, response, bytes([0x51, reset_type]))
    
    def validate_clear_diagnostic_information(self, response: bytes) -> Dict:
        """Validate 0x14 Clear Diagnostic Information response"""
        return self.validate_service_response(None, response, bytes([0x54]))
    
    def validate_read_dtc_information(self, response: bytes, sub_function: int) -> Dict:
        """Validate 0x19 Read DTC Information response"""
        expected_prefix = bytes([0x59, sub_function])
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_read_data_by_identifier(self, response: bytes, did: int) -> Dict:
        """Validate 0x22 Read Data By Identifier response"""
        expected_prefix = bytes([0x62]) + did.to_bytes(2, 'big')
        result = self.validate_service_response(None, response, expected_prefix)
        if result['positive'] and len(response) > 3:
            result['data'] = response[3:]
        return result
    
    def validate_communication_control(self, response: bytes, control_type: int) -> Dict:
        """Validate 0x28 Communication Control response"""
        expected_prefix = bytes([0x68, control_type])
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_write_data_by_identifier(self, response: bytes, did: int) -> Dict:
        """Validate 0x2E Write Data By Identifier response"""
        expected_prefix = bytes([0x6E]) + did.to_bytes(2, 'big')
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_input_output_control(self, response: bytes, did: int, control_param: int) -> Dict:
        """Validate 0x2F Input Output Control response"""
        expected_prefix = bytes([0x6F]) + did.to_bytes(2, 'big') + bytes([control_param])
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_routine_control(self, response: bytes, routine_id: int, sub_function: int) -> Dict:
        """Validate 0x31 Routine Control response"""
        expected_prefix = bytes([0x71, sub_function]) + routine_id.to_bytes(2, 'big')
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_request_download(self, response: bytes) -> Dict:
        """Validate 0x34 Request Download response"""
        result = self.validate_service_response(None, response, bytes([0x74]))
        if result['positive'] and len(response) >= 4:
            result['max_block_length'] = int.from_bytes(response[2:], 'big')
        return result
    
    def validate_transfer_data(self, response: bytes, block_seq_counter: int) -> Dict:
        """Validate 0x36 Transfer Data response"""
        expected_prefix = bytes([0x76, block_seq_counter])
        return self.validate_service_response(None, response, expected_prefix)
    
    def validate_request_transfer_exit(self, response: bytes) -> Dict:
        """Validate 0x37 Request Transfer Exit response"""
        return self.validate_service_response(None, response, bytes([0x77]))
    
    def validate_tester_present(self, response: bytes, sub_function: int = 0x00) -> Dict:
        """Validate 0x3E Tester Present response"""
        return self.validate_service_response(None, response, bytes([0x7E, sub_function]))
    
    def validate_security_access(self, response: bytes, sub_function: int) -> Dict:
        """Validate 0x27 Security Access response"""
        expected_prefix = bytes([0x67, sub_function])
        result = self.validate_service_response(None, response, expected_prefix)
        if result['positive'] and sub_function % 2 == 1 and len(response) > 2:
            result['seed'] = response[2:]
        return result