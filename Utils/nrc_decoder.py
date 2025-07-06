# utils/nrc_decoder.py
def decode_nrc(nrc_byte):
    nrc_dict = {
        0x10: "General Reject",
        0x11: "Service Not Supported",
        0x12: "Sub-function Not Supported",
        0x13: "Incorrect Message Length or Invalid Format",
        # Add more from ISO 14229 Annex A
    }
    return nrc_dict.get(nrc_byte, "Unknown NRC")
