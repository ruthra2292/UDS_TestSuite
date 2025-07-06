# Utils/doip_handler.py
import socket
import struct
import time
from typing import Optional, Tuple

class DoIPHandler:
    """DoIP (Diagnostic over IP) protocol handler"""
    
    # DoIP Header constants
    DOIP_VERSION = 0x02
    DOIP_INVERSE_VERSION = 0xFD
    DOIP_HEADER_SIZE = 8
    
    # DoIP Payload Types
    DOIP_DIAG_MESSAGE = 0x8001
    DOIP_DIAG_MESSAGE_ACK = 0x8002
    DOIP_DIAG_MESSAGE_NACK = 0x8003
    DOIP_ALIVE_CHECK_REQUEST = 0x0007
    DOIP_ALIVE_CHECK_RESPONSE = 0x0008
    
    def __init__(self, target_ip: str, target_port: int = 13400, source_addr: int = 0x0E00, target_addr: int = 0x1234):
        self.target_ip = target_ip
        self.target_port = target_port
        self.source_addr = source_addr
        self.target_addr = target_addr
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to DoIP gateway"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.target_ip, self.target_port))
            self.connected = True
            return True
        except Exception as e:
            print(f"DoIP connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from DoIP gateway"""
        if self.socket:
            self.socket.close()
            self.connected = False
    
    def _create_doip_header(self, payload_type: int, payload_length: int) -> bytes:
        """Create DoIP header"""
        return struct.pack('>BBHI', 
                          self.DOIP_VERSION, 
                          self.DOIP_INVERSE_VERSION,
                          payload_type, 
                          payload_length)
    
    def _parse_doip_header(self, header: bytes) -> Tuple[int, int, int]:
        """Parse DoIP header"""
        version, inv_version, payload_type, payload_length = struct.unpack('>BBHI', header)
        return version, payload_type, payload_length
    
    def send_diagnostic_message(self, uds_data: bytes) -> Optional[bytes]:
        """Send UDS diagnostic message over DoIP"""
        if not self.connected:
            return None
        
        # Create DoIP diagnostic message payload
        payload = struct.pack('>HH', self.source_addr, self.target_addr) + uds_data
        header = self._create_doip_header(self.DOIP_DIAG_MESSAGE, len(payload))
        
        try:
            # Send DoIP message
            self.socket.send(header + payload)
            
            # Receive response
            response_header = self.socket.recv(self.DOIP_HEADER_SIZE)
            if len(response_header) != self.DOIP_HEADER_SIZE:
                return None
            
            version, payload_type, payload_length = self._parse_doip_header(response_header)
            
            if payload_type == self.DOIP_DIAG_MESSAGE_ACK:
                # Receive diagnostic response
                response_payload = self.socket.recv(payload_length)
                if len(response_payload) >= 4:
                    # Skip source/target addresses, return UDS data
                    return response_payload[4:]
            
            return None
            
        except Exception as e:
            print(f"DoIP communication error: {e}")
            return None

class DoSOADHandler:
    """DoSOAD (Diagnostic over Service Oriented Architecture Daemon) handler"""
    
    def __init__(self, service_id: int = 0x1234, instance_id: int = 0x5678):
        self.service_id = service_id
        self.instance_id = instance_id
        self.session_id = 0
    
    def create_soad_request(self, uds_data: bytes) -> bytes:
        """Create DoSOAD request message"""
        # SOME/IP header for DoSOAD (16 bytes)
        someip_header = struct.pack('>HHHLBBBB',
                                   self.service_id,    # Service ID (2 bytes)
                                   0x0001,             # Method ID (2 bytes)
                                   len(uds_data) + 8,  # Length (4 bytes)
                                   0x0000,             # Client ID (2 bytes)
                                   self.session_id,    # Session ID (1 byte)
                                   0x01,               # Protocol Version (1 byte)
                                   0x00,               # Interface Version (1 byte)
                                   0x00)               # Message Type (1 byte)
        
        self.session_id = (self.session_id + 1) % 256
        return someip_header + uds_data
    
    def parse_soad_response(self, soad_data: bytes) -> Optional[bytes]:
        """Parse DoSOAD response and extract UDS data"""
        if len(soad_data) < 16:  # Minimum SOME/IP header size
            return None
        
        # Parse SOME/IP header (16 bytes)
        service_id, method_id, length, client_id, session_id, proto_ver, intf_ver, msg_type = \
            struct.unpack('>HHHLBBBB', soad_data[:16])
        
        # Extract UDS payload
        if len(soad_data) > 16:
            return soad_data[16:]
        
        return None

def create_doip_connection(ip: str, port: int = 13400) -> DoIPHandler:
    """Factory function to create DoIP connection"""
    handler = DoIPHandler(ip, port)
    if handler.connect():
        return handler
    return None

def create_dosoad_handler(service_id: int = 0x1234) -> DoSOADHandler:
    """Factory function to create DoSOAD handler"""
    return DoSOADHandler(service_id)