# run_complete_tests.py
"""
Complete UDS Test Suite Runner - All ISO 14229 Services
Executes comprehensive UDS service tests with proper encoding handling
"""

import sys
import os
import time
from typing import List, Dict

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all test modules
from test_services.test_diagnostic_session_control_new import DiagnosticSessionControlTest
from test_services.test_ecu_reset import ECUResetTest
from test_services.test_clear_diagnostic_information import ClearDiagnosticInformationTest
from test_services.test_read_dtc_information import ReadDTCInformationTest
from test_services.test_read_data_by_identifier import ReadDataByIdentifierTest
from test_services.test_communication_control import CommunicationControlTest
from test_services.test_write_data_by_identifier import WriteDataByIdentifierTest
from test_services.test_input_output_control import InputOutputControlTest
from test_services.test_routine_control import RoutineControlTest
from test_services.test_request_download import RequestDownloadTest
from test_services.test_transfer_data import TransferDataTest
from test_services.test_request_transfer_exit import RequestTransferExitTest
from test_services.test_tester_present import TesterPresentTest
from test_services.test_security_access import SecurityAccessTest
from Utils.uds_utils import TestLogger

class CompleteUDSTestSuite:
    """Complete UDS Test Suite Runner - All ISO 14229 Services"""
    
    def __init__(self):
        self.master_logger = TestLogger()
        self.test_classes = [
            ("Diagnostic Session Control (0x10)", DiagnosticSessionControlTest),
            ("ECU Reset (0x11)", ECUResetTest),
            ("Clear Diagnostic Information (0x14)", ClearDiagnosticInformationTest),
            ("Read DTC Information (0x19)", ReadDTCInformationTest),
            ("Read Data By Identifier (0x22)", ReadDataByIdentifierTest),
            ("Communication Control (0x28)", CommunicationControlTest),
            ("Write Data By Identifier (0x2E)", WriteDataByIdentifierTest),
            ("Input Output Control (0x2F)", InputOutputControlTest),
            ("Routine Control (0x31)", RoutineControlTest),
            ("Request Download (0x34)", RequestDownloadTest),
            ("Transfer Data (0x36)", TransferDataTest),
            ("Request Transfer Exit (0x37)", RequestTransferExitTest),
            ("Tester Present (0x3E)", TesterPresentTest),
            ("Security Access (0x27)", SecurityAccessTest),
        ]
        self.results = {}
    
    def run_single_test_suite(self, name: str, test_class) -> Dict:
        """Run a single test suite and capture results"""
        print(f"\n{'='*80}")
        print(f"RUNNING: {name}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            test_instance = test_class()
            test_instance.run_all_tests()
            
            summary = test_instance.logger.get_summary()
            summary['duration'] = time.time() - start_time
            summary['status'] = 'COMPLETED'
            summary['error'] = None
            
        except Exception as e:
            summary = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0,
                'duration': time.time() - start_time,
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"ERROR in {name}: {e}")
        
        return summary
    
    def run_all_tests(self):
        """Run all UDS test suites"""
        print("="*80)
        print("COMPLETE UDS DIAGNOSTIC TEST SUITE - ISO 14229 COMPLIANCE")
        print("="*80)
        print(f"Starting comprehensive UDS testing at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {len(self.test_classes)} UDS services")
        
        overall_start = time.time()
        
        for name, test_class in self.test_classes:
            self.results[name] = self.run_single_test_suite(name, test_class)
        
        overall_duration = time.time() - overall_start
        self.generate_final_report(overall_duration)
    
    def generate_final_report(self, total_duration: float):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("COMPLETE UDS TEST SUITE REPORT")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        completed_suites = 0
        error_suites = 0
        
        print(f"{'Service':<40} {'Tests':<8} {'Passed':<8} {'Failed':<8} {'Rate':<8} {'Status':<12}")
        print("-" * 80)
        
        for name, result in self.results.items():
            total_tests += result['total']
            total_passed += result['passed']
            total_failed += result['failed']
            
            if result['status'] == 'COMPLETED':
                completed_suites += 1
            else:
                error_suites += 1
            
            if result['status'] == 'COMPLETED' and result['pass_rate'] == 100:
                status_indicator = "[PASS]"
            elif result['status'] == 'COMPLETED':
                status_indicator = "[WARN]"
            else:
                status_indicator = "[FAIL]"
            
            print(f"{name:<40} {result['total']:<8} {result['passed']:<8} {result['failed']:<8} {result['pass_rate']:<7.1f}% {status_indicator} {result['status']:<8}")
        
        print("-" * 80)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"{'TOTAL':<40} {total_tests:<8} {total_passed:<8} {total_failed:<8} {overall_pass_rate:<7.1f}%")
        
        print(f"\nCOMPLETE TEST SUMMARY:")
        print(f"* Total UDS Services Tested: {len(self.test_classes)}")
        print(f"* Services Completed Successfully: {completed_suites}")
        print(f"* Services Failed with Errors: {error_suites}")
        print(f"* Total Individual Tests: {total_tests}")
        print(f"* Overall Pass Rate: {overall_pass_rate:.1f}%")
        print(f"* Total Execution Time: {total_duration:.2f} seconds")
        
        # Service coverage report
        print(f"\nUDS SERVICE COVERAGE:")
        services_tested = [
            "0x10 - Diagnostic Session Control",
            "0x11 - ECU Reset", 
            "0x14 - Clear Diagnostic Information",
            "0x19 - Read DTC Information",
            "0x22 - Read Data By Identifier",
            "0x27 - Security Access",
            "0x28 - Communication Control",
            "0x2E - Write Data By Identifier", 
            "0x2F - Input Output Control",
            "0x31 - Routine Control",
            "0x34 - Request Download",
            "0x36 - Transfer Data",
            "0x37 - Request Transfer Exit",
            "0x3E - Tester Present"
        ]
        
        for service in services_tested:
            print(f"  [X] {service}")
        
        if error_suites > 0:
            print(f"\nERROR DETAILS:")
            for name, result in self.results.items():
                if result['status'] == 'ERROR':
                    print(f"* {name}: {result['error']}")
        
        print(f"\nCOMPLIANCE ASSESSMENT:")
        if overall_pass_rate == 100:
            print("EXCELLENT: Full ISO 14229 compliance achieved!")
        elif overall_pass_rate >= 95:
            print("VERY GOOD: Near-complete ISO 14229 compliance")
        elif overall_pass_rate >= 90:
            print("GOOD: Strong ISO 14229 compliance with minor issues")
        elif overall_pass_rate >= 75:
            print("ACCEPTABLE: Basic ISO 14229 compliance - review failed tests")
        else:
            print("NEEDS IMPROVEMENT: Significant compliance issues detected")
        
        print("="*80)

def main():
    """Main execution function"""
    try:
        suite = CompleteUDSTestSuite()
        suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user.")
    except Exception as e:
        print(f"\nFatal error during test execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()