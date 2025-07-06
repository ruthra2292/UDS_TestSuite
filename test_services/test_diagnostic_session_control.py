# test_services/test_diagnostic_session_control.py
import time
from uds_validator import UDSValidator
import udsoncan
from udsoncan.connections import IsoTPSocketConnection

def test_diagnostic_session_control():
    conn = IsoTPSocketConnection('192.168.0.10', 13400)  # DOIP
    validator = UDSValidator()

    with udsoncan.Client(conn, request_timeout=2) as client:
        try:
            request_sid = bytes([0x10, 0x03])  # Extended diagnostic session
            expected_response_prefix = bytes([0x50, 0x03])

            response = client.send_request(request_sid)
            validator.log_result(request_sid, response, expected_response_prefix)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_diagnostic_session_control()
