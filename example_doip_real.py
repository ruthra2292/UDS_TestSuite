# example_doip_real.py
"""
Real DoIP/DoSOAD ECU Integration Example
Shows how to use the UDS test suite with real ECU connections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Utils.doip_handler import DoIPHandler, DoSOADHandler
from uds_validator_extended import UDSValidator
from Utils.uds_utils import TestLogger

class RealDoIPTest:
    """Example class for real DoIP ECU testing"""
    
    def __init__(self, ecu_ip: str, ecu_port: int = 13400):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.doip_handler = DoIPHandler(ecu_ip, ecu_port, source_addr=0x0E00, target_addr=0x1234)
        self.dosoad_handler = DoSOADHandler(service_id=0x1234, instance_id=0x5678)
    
    def test_doip_connection(self):
        """Test real DoIP connection and basic UDS services"""
        print(f"\n{'='*60}")
        print(f"TESTING REAL DOIP ECU CONNECTION")
        print(f"Target: {self.doip_handler.target_ip}:{self.doip_handler.target_port}")
        print(f"{'='*60}")
        
        # Test connection
        if not self.doip_handler.connect():
            print("❌ Failed to connect to DoIP ECU")
            self.logger.log_test("DoIP Connection", False, "Connection failed")
            return
        
        print("✅ DoIP connection established")
        self.logger.log_test("DoIP Connection", True, "Connected successfully")
        
        try:
            # Test 1: Extended diagnostic session
            print("\n1. Testing Extended Diagnostic Session...")
            request = bytes([0x10, 0x03])
            response = self.doip_handler.send_diagnostic_message(request)
            
            if response:
                result = self.validator.validate_diagnostic_session_control(response, 0x03)
                self.validator.log_test_result("DoIP Extended Session", request, response, validation_result=result)
                self.logger.log_test("DoIP Extended Session", result['positive'], result['message'])
            else:
                self.logger.log_test("DoIP Extended Session", False, "No response received")
            
            # Test 2: Read VIN
            print("\n2. Testing Read VIN...")
            request = bytes([0x22, 0xF1, 0x90])
            response = self.doip_handler.send_diagnostic_message(request)
            
            if response:
                result = self.validator.validate_read_data_by_identifier(response, 0xF190)
                if result['positive'] and 'data' in result:
                    vin = result['data'].decode('ascii', errors='ignore')
                    self.logger.log_test("DoIP Read VIN", result['valid'], f"VIN: {vin}")
                else:
                    self.logger.log_test("DoIP Read VIN", False, result['message'])
            else:
                self.logger.log_test("DoIP Read VIN", False, "No response received")
            
            # Test 3: Tester Present
            print("\n3. Testing Tester Present...")
            request = bytes([0x3E, 0x00])
            response = self.doip_handler.send_diagnostic_message(request)
            
            if response:
                result = self.validator.validate_tester_present(response, 0x00)
                self.logger.log_test("DoIP Tester Present", result['positive'], result['message'])
            else:
                self.logger.log_test("DoIP Tester Present", False, "No response received")
            
            # Test 4: Read DTCs
            print("\n4. Testing Read DTC Information...")
            request = bytes([0x19, 0x02, 0x00])  # Report DTCs by status mask
            response = self.doip_handler.send_diagnostic_message(request)
            
            if response:
                result = self.validator.validate_read_dtc_information(response, 0x02)
                if result['positive']:
                    dtc_data = response[3:] if len(response) > 3 else b''
                    self.logger.log_test("DoIP Read DTCs", result['valid'], f"DTC data: {dtc_data.hex().upper()}")
                else:
                    self.logger.log_test("DoIP Read DTCs", False, result['message'])
            else:
                self.logger.log_test("DoIP Read DTCs", False, "No response received")
                
        finally:
            self.doip_handler.disconnect()
            print("\n✅ DoIP connection closed")
        
        self.logger.print_summary()

class MockDoSOADTest:
    """Example DoSOAD testing with mock responses"""
    
    def __init__(self):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.dosoad_handler = DoSOADHandler()
    
    def mock_dosoad_communication(self, uds_request: bytes) -> bytes:
        """Mock DoSOAD communication for testing"""
        # Create SOME/IP request
        soad_request = self.dosoad_handler.create_soad_request(uds_request)
        
        # Mock SOME/IP response based on UDS request
        if uds_request == bytes([0x10, 0x03]):
            uds_response = bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])
        elif uds_request == bytes([0x22, 0xF1, 0x90]):
            uds_response = bytes([0x62, 0xF1, 0x90]) + b"DOSOAD_VIN_TEST123"
        elif uds_request == bytes([0x3E, 0x00]):
            uds_response = bytes([0x7E, 0x00])
        else:
            uds_response = bytes([0x7F, uds_request[0], 0x11])
        
        # Create mock SOME/IP response
        someip_header = bytes([0x12, 0x34, 0x80, 0x01,  # Service ID + Method ID
                              0x00, len(uds_response) + 8,  # Length
                              0x00, 0x01,  # Client ID + Session ID
                              0x01, 0x00, 0x00, 0x00])  # Version + Message Type
        
        soad_response = someip_header + uds_response
        
        # Parse response to get UDS data
        return self.dosoad_handler.parse_soad_response(soad_response)
    
    def test_dosoad_services(self):
        """Test DoSOAD communication with various UDS services"""
        print(f"\n{'='*60}")
        print(f"TESTING DOSOAD COMMUNICATION (MOCK)")
        print(f"{'='*60}")
        
        # Test 1: Extended session
        request = bytes([0x10, 0x03])
        response = self.mock_dosoad_communication(request)
        result = self.validator.validate_diagnostic_session_control(response, 0x03)
        self.logger.log_test("DoSOAD Extended Session", result['positive'], result['message'])
        
        # Test 2: Read VIN
        request = bytes([0x22, 0xF1, 0x90])
        response = self.mock_dosoad_communication(request)
        result = self.validator.validate_read_data_by_identifier(response, 0xF190)
        if result['positive'] and 'data' in result:
            vin = result['data'].decode('ascii', errors='ignore')
            self.logger.log_test("DoSOAD Read VIN", result['valid'], f"VIN: {vin}")
        
        # Test 3: Tester Present
        request = bytes([0x3E, 0x00])
        response = self.mock_dosoad_communication(request)
        result = self.validator.validate_tester_present(response, 0x00)
        self.logger.log_test("DoSOAD Tester Present", result['positive'], result['message'])
        
        self.logger.print_summary()

def main():
    """Main execution with DoIP and DoSOAD examples"""
    
    print("UDS Test Suite - DoIP/DoSOAD Integration Examples")
    print("=" * 60)
    
    # Example 1: Mock DoSOAD testing (always works)
    print("\n🔧 Running DoSOAD Mock Tests...")
    dosoad_test = MockDoSOADTest()
    dosoad_test.test_dosoad_services()
    
    # Example 2: Real DoIP testing (requires real ECU)
    print("\n🌐 Attempting Real DoIP Connection...")
    print("Note: Change IP address to match your ECU")
    
    # Uncomment and modify IP address for real testing
    # doip_test = RealDoIPTest("192.168.1.100")  # Change to your ECU IP
    # doip_test.test_doip_connection()
    
    print("\n" + "=" * 60)
    print("DoIP/DoSOAD Integration Examples Completed!")
    print("\nTo test with real ECU:")
    print("1. Uncomment the real DoIP test lines above")
    print("2. Change IP address to match your ECU")
    print("3. Ensure ECU is connected and accessible")
    print("4. Run the script again")

if __name__ == "__main__":
    main()