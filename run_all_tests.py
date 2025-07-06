# run_all_tests.py
"""
Master test runner for UDS Test Suite
Executes all UDS service tests and provides comprehensive reporting
"""

import sys
import os
import time
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all test modules
from test_services.test_diagnostic_session_control_new import DiagnosticSessionControlTest
from test_services.test_ecu_reset import ECUResetTest
from test_services.test_read_data_by_identifier import ReadDataByIdentifierTest
from test_services.test_write_data_by_identifier import WriteDataByIdentifierTest
from test_services.test_routine_control import RoutineControlTest
from test_services.test_tester_present import TesterPresentTest
from test_services.test_security_access import SecurityAccessTest
from Utils.uds_utils import TestLogger

class UDSTestSuite:
    """Master UDS Test Suite Runner"""
    
    def __init__(self):
        self.master_logger = TestLogger()
        self.test_classes = [
            ("Diagnostic Session Control (0x10)", DiagnosticSessionControlTest),
            ("ECU Reset (0x11)", ECUResetTest),
            ("Read Data By Identifier (0x22)", ReadDataByIdentifierTest),
            ("Write Data By Identifier (0x2E)", WriteDataByIdentifierTest),
            ("Routine Control (0x31)", RoutineControlTest),
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
            # Create test instance and run tests
            test_instance = test_class()
            test_instance.run_all_tests()
            
            # Get results from the test logger
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
        print("UDS DIAGNOSTIC TEST SUITE - ISO 14229 COMPLIANCE TESTING")
        print("="*80)
        print(f"Starting comprehensive UDS testing at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing {len(self.test_classes)} UDS services")
        
        overall_start = time.time()
        
        # Run each test suite
        for name, test_class in self.test_classes:
            self.results[name] = self.run_single_test_suite(name, test_class)
        
        overall_duration = time.time() - overall_start
        
        # Generate comprehensive report
        self.generate_final_report(overall_duration)
    
    def generate_final_report(self, total_duration: float):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("FINAL TEST REPORT")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        completed_suites = 0
        error_suites = 0
        
        print(f"{'Service':<35} {'Tests':<8} {'Passed':<8} {'Failed':<8} {'Rate':<8} {'Status':<12}")
        print("-" * 80)
        
        for name, result in self.results.items():
            total_tests += result['total']
            total_passed += result['passed']
            total_failed += result['failed']
            
            if result['status'] == 'COMPLETED':
                completed_suites += 1
            else:
                error_suites += 1
            
            status_color = "✅" if result['status'] == 'COMPLETED' and result['pass_rate'] == 100 else "⚠️" if result['status'] == 'COMPLETED' else "❌"
            
            print(f"{name:<35} {result['total']:<8} {result['passed']:<8} {result['failed']:<8} {result['pass_rate']:<7.1f}% {status_color} {result['status']:<10}")
        
        print("-" * 80)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"{'TOTAL':<35} {total_tests:<8} {total_passed:<8} {total_failed:<8} {overall_pass_rate:<7.1f}%")
        
        print(f"\nSUMMARY:")
        print(f"• Total Test Suites: {len(self.test_classes)}")
        print(f"• Completed Successfully: {completed_suites}")
        print(f"• Failed with Errors: {error_suites}")
        print(f"• Total Individual Tests: {total_tests}")
        print(f"• Overall Pass Rate: {overall_pass_rate:.1f}%")
        print(f"• Total Execution Time: {total_duration:.2f} seconds")
        
        # Detailed error report
        if error_suites > 0:
            print(f"\nERROR DETAILS:")
            for name, result in self.results.items():
                if result['status'] == 'ERROR':
                    print(f"• {name}: {result['error']}")
        
        # Recommendations
        print(f"\nRECOMMENDations:")
        if overall_pass_rate == 100:
            print("🎉 All tests passed! Your UDS implementation is compliant with ISO 14229.")
        elif overall_pass_rate >= 90:
            print("✅ Excellent compliance! Minor issues detected - review failed tests.")
        elif overall_pass_rate >= 75:
            print("⚠️  Good compliance with some issues - review and fix failed tests.")
        else:
            print("❌ Significant compliance issues detected - thorough review required.")
        
        print("="*80)

def main():
    """Main execution function"""
    try:
        suite = UDSTestSuite()
        suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user.")
    except Exception as e:
        print(f"\nFatal error during test execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()