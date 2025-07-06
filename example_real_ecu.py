# example_real_ecu.py
"""
Example script showing how to integrate UDS Test Suite with real ECU connections
Supports CAN, ISO-TP, and DoIP transport layers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from uds_validator import UDSValidator
from Utils.uds_utils import TestLogger, retry_on_pending

# Uncomment the transport layer you want to use:

# For DoIP (Diagnostic over IP)
# import udsoncan
# from udsoncan.connections import IsoTPSocketConnection

# For CAN with ISO-TP
# import isotp
# import udsoncan
# from udsoncan.connections import PythonIsoTpConnection

class RealECUTest:
    """Example class for testing with real ECU connections"""
    
    def __init__(self, connection_type="mock"):
        self.validator = UDSValidator()
        self.logger = TestLogger()
        self.connection = None
        self.connection_type = connection_type
        
        if connection_type != "mock":
            self.setup_connection(connection_type)
    
    def setup_connection(self, connection_type):
        """Setup real ECU connection based on transport type"""
        
        if connection_type == "doip":
            # DoIP connection example
            try:
                # import udsoncan
                # from udsoncan.connections import IsoTPSocketConnection
                # self.connection = IsoTPSocketConnection('192.168.1.100', 13400)
                print("DoIP connection setup (uncomment imports to use)")
            except ImportError:
                print("udsoncan not installed. Run: pip install udsoncan")
                
        elif connection_type == "can":
            # CAN with ISO-TP example
            try:
                # import isotp
                # import udsoncan
                # from udsoncan.connections import PythonIsoTpConnection
                # 
                # # Setup ISO-TP socket
                # isotp_socket = isotp.socket.IsoTpSocket("can0", txid=0x123, rxid=0x456)
                # self.connection = PythonIsoTpConnection(isotp_socket)
                print("CAN connection setup (uncomment imports to use)")
            except ImportError:
                print("python-isotp not installed. Run: pip install python-isotp")
        
        else:
            print(f"Unknown connection type: {connection_type}")
    
    @retry_on_pending
    def send_uds_request(self, request: bytes) -> bytes:
        """Send UDS request to real ECU with retry logic"""
        if self.connection is None:
            # Mock responses for demonstration
            return self.mock_response(request)
        
        try:
            # Real ECU communication
            # with udsoncan.Client(self.connection, request_timeout=2) as client:
            #     response = client.send_request(request)
            #     return response
            pass
        except Exception as e:
            print(f"Communication error: {e}")
            return bytes([0x7F, request[0], 0x25])  # No response from subnet component
    
    def mock_response(self, request: bytes) -> bytes:
        """Mock responses for testing without real ECU"""
        if request == bytes([0x10, 0x03]):  # Extended session
            return bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])
        elif request == bytes([0x22, 0xF1, 0x90]):  # Read VIN
            return bytes([0x62, 0xF1, 0x90]) + b"WVWZZZ1JZ3W386752"
        elif request == bytes([0x3E, 0x00]):  # Tester present
            return bytes([0x7E, 0x00])
        else:
            return bytes([0x7F, request[0], 0x11])  # Service not supported
    
    def test_ecu_communication(self):
        """Test basic ECU communication"""
        print(f"\n{'='*60}")
        print(f"TESTING ECU COMMUNICATION ({self.connection_type.upper()})")
        print(f"{'='*60}")
        
        # Test 1: Extended diagnostic session
        print("\n1. Testing Extended Diagnostic Session...")
        request = bytes([0x10, 0x03])
        response = self.send_uds_request(request)
        
        result = self.validator.validate_diagnostic_session_control(response, 0x03)
        self.validator.log_test_result("Extended Session", request, response, validation_result=result)
        
        self.logger.log_test(
            "Extended Session",
            result['positive'] and result['valid'],
            f"Session timing: {result.get('timing', 'N/A')}"
        )
        
        # Test 2: Read VIN
        print("\n2. Testing Read VIN...")
        request = bytes([0x22, 0xF1, 0x90])
        response = self.send_uds_request(request)
        
        result = self.validator.validate_read_data_by_identifier(response, 0xF190)
        self.validator.log_test_result("Read VIN", request, response, validation_result=result)
        
        if result['positive'] and 'data' in result:
            vin = result['data'].decode('ascii', errors='ignore')
            self.logger.log_test("Read VIN", result['valid'], f"VIN: {vin}")
        else:
            self.logger.log_test("Read VIN", False, result['message'])
        
        # Test 3: Tester Present
        print("\n3. Testing Tester Present...")
        request = bytes([0x3E, 0x00])
        response = self.send_uds_request(request)
        
        result = self.validator.validate_tester_present(response, 0x00)
        self.validator.log_test_result("Tester Present", request, response, validation_result=result)
        
        self.logger.log_test(
            "Tester Present",
            result['positive'] and result['valid'],
            "Keep-alive successful"
        )
        
        # Print summary
        self.logger.print_summary()

def main():
    """Main execution with different connection examples"""
    
    print("UDS Test Suite - Real ECU Integration Example")
    print("=" * 50)
    
    # Example 1: Mock testing (no real ECU needed)
    print("\n🔧 Running with MOCK ECU responses...")
    mock_test = RealECUTest("mock")
    mock_test.test_ecu_communication()
    
    # Example 2: DoIP connection (uncomment to use)
    # print("\n🌐 Running with DoIP connection...")
    # doip_test = RealECUTest("doip")
    # doip_test.test_ecu_communication()
    
    # Example 3: CAN connection (uncomment to use)
    # print("\n🚗 Running with CAN connection...")
    # can_test = RealECUTest("can")
    # can_test.test_ecu_communication()
    
    print("\n" + "=" * 50)
    print("Integration example completed!")
    print("\nTo use with real ECUs:")
    print("1. Uncomment the appropriate import statements")
    print("2. Configure your connection parameters")
    print("3. Update the setup_connection() method")
    print("4. Run the script with your ECU connected")

if __name__ == "__main__":
    main()