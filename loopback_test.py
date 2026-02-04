#!/usr/bin/env python3
"""
NI PCIe-6535 Loopback Test Program

This program tests the port read functionality of the NI PCIe-6535 board
by performing loopback tests between ports 1&3 and ports 2&4.

Hardware Setup:
- Connect Port 1 to Port 3 (all 8 channels)
- Connect Port 2 to Port 4 (all 8 channels)

The test will:
1. Write patterns to Port 1 and verify on Port 3
2. Write patterns to Port 3 and verify on Port 1
3. Write patterns to Port 2 and verify on Port 4
4. Write patterns to Port 4 and verify on Port 2

Test patterns include:
- All zeros (0x00)
- All ones (0xFF)
- Alternating bits (0xAA, 0x55)
- Walking 1s (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)
- Walking 0s (0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F)
"""

import nidaqmx
from nidaqmx.constants import LineGrouping
import time
import sys


class NI6535LoopbackTest:
    def __init__(self, device_name="Dev1"):
        """
        Initialize the loopback test.
        
        Args:
            device_name: Name of the NI DAQ device (default: "Dev1")
        """
        self.device_name = device_name
        self.test_results = []
        
    def get_test_patterns(self):
        """
        Generate a comprehensive set of test patterns.
        
        Returns:
            List of 8-bit test patterns
        """
        patterns = []
        
        # Basic patterns
        patterns.append(0x00)  # All zeros
        patterns.append(0xFF)  # All ones
        patterns.append(0xAA)  # Alternating 10101010
        patterns.append(0x55)  # Alternating 01010101
        
        # Walking 1s
        for i in range(8):
            patterns.append(1 << i)
            
        # Walking 0s
        for i in range(8):
            patterns.append(0xFF ^ (1 << i))
            
        # Additional patterns
        patterns.append(0x0F)  # Lower nibble
        patterns.append(0xF0)  # Upper nibble
        patterns.append(0x33)  # 00110011
        patterns.append(0xCC)  # 11001100
        
        return patterns
    
    def write_port(self, port_number, value):
        """
        Write a value to the specified port.
        
        Args:
            port_number: Port number (0-3)
            value: 8-bit value to write
        """
        with nidaqmx.Task() as task:
            # Add digital output lines for the entire port
            task.do_channels.add_do_chan(
                f"{self.device_name}/port{port_number}",
                line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
            )
            task.write(value, auto_start=True)
            # Small delay to ensure data is stable
            time.sleep(0.001)
    
    def read_port(self, port_number):
        """
        Read a value from the specified port.
        
        Args:
            port_number: Port number (0-3)
            
        Returns:
            8-bit value read from the port
        """
        with nidaqmx.Task() as task:
            # Add digital input lines for the entire port
            task.di_channels.add_di_chan(
                f"{self.device_name}/port{port_number}",
                line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
            )
            # Small delay to ensure data is stable
            time.sleep(0.001)
            value = task.read()
            return value
    
    def test_port_pair(self, write_port_num, read_port_num, direction_name):
        """
        Test a port pair with all test patterns.
        
        Args:
            write_port_num: Port number to write to
            read_port_num: Port number to read from
            direction_name: Description of test direction
            
        Returns:
            Tuple of (passed, failed) test counts
        """
        patterns = self.get_test_patterns()
        passed = 0
        failed = 0
        
        print(f"\n{direction_name}")
        print("-" * 60)
        
        for pattern in patterns:
            try:
                # Write pattern to output port
                self.write_port(write_port_num, pattern)
                
                # Read from input port
                read_value = self.read_port(read_port_num)
                
                # Compare
                if read_value == pattern:
                    passed += 1
                    result = "PASS"
                    self.test_results.append({
                        'test': direction_name,
                        'pattern': pattern,
                        'expected': pattern,
                        'actual': read_value,
                        'result': 'PASS'
                    })
                else:
                    failed += 1
                    result = "FAIL"
                    self.test_results.append({
                        'test': direction_name,
                        'pattern': pattern,
                        'expected': pattern,
                        'actual': read_value,
                        'result': 'FAIL'
                    })
                    
                print(f"  Pattern 0x{pattern:02X}: Expected 0x{pattern:02X}, "
                      f"Read 0x{read_value:02X} [{result}]")
                
            except Exception as e:
                failed += 1
                print(f"  Pattern 0x{pattern:02X}: ERROR - {str(e)}")
                self.test_results.append({
                    'test': direction_name,
                    'pattern': pattern,
                    'expected': pattern,
                    'actual': None,
                    'result': 'ERROR',
                    'error': str(e)
                })
        
        return passed, failed
    
    def run_tests(self):
        """
        Run all loopback tests.
        
        Returns:
            True if all tests passed, False otherwise
        """
        print("=" * 60)
        print("NI PCIe-6535 Loopback Test")
        print("=" * 60)
        print(f"Device: {self.device_name}")
        print("\nTest Configuration:")
        print("  - Port 1 (output) <-> Port 3 (input)")
        print("  - Port 2 (output) <-> Port 4 (input)")
        print(f"\nTotal test patterns: {len(self.get_test_patterns())}")
        
        total_passed = 0
        total_failed = 0
        
        # Test Port 1 -> Port 3
        passed, failed = self.test_port_pair(1, 3, "Port 1 -> Port 3")
        total_passed += passed
        total_failed += failed
        
        # Test Port 3 -> Port 1
        passed, failed = self.test_port_pair(3, 1, "Port 3 -> Port 1")
        total_passed += passed
        total_failed += failed
        
        # Test Port 2 -> Port 4
        passed, failed = self.test_port_pair(2, 4, "Port 2 -> Port 4")
        total_passed += passed
        total_failed += failed
        
        # Test Port 4 -> Port 2
        passed, failed = self.test_port_pair(4, 2, "Port 4 -> Port 2")
        total_passed += passed
        total_failed += failed
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total Tests:  {total_passed + total_failed}")
        print(f"Passed:       {total_passed}")
        print(f"Failed:       {total_failed}")
        total_tests = total_passed + total_failed
        if total_tests > 0:
            print(f"Success Rate: {100.0 * total_passed / total_tests:.1f}%")
        else:
            print("Success Rate: N/A (no tests run)")
        print("=" * 60)
        
        if total_failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['result'] != 'PASS':
                    actual_str = f"0x{result['actual']:02X}" if result['actual'] is not None else 'ERROR'
                    print(f"  {result['test']}: Pattern 0x{result['pattern']:02X} - "
                          f"Expected 0x{result['expected']:02X}, "
                          f"Got {actual_str}")
        
        return total_failed == 0


def main():
    """Main function to run the loopback test."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='NI PCIe-6535 Loopback Test Program',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Hardware Setup:
  Connect the following ports for loopback testing:
    - Port 1 to Port 3 (all 8 channels)
    - Port 2 to Port 4 (all 8 channels)
    
Examples:
  # Run test with default device (Dev1)
  python loopback_test.py
  
  # Run test with specific device
  python loopback_test.py --device Dev2
        """
    )
    
    parser.add_argument(
        '--device',
        default='Dev1',
        help='NI DAQ device name (default: Dev1)'
    )
    
    args = parser.parse_args()
    
    try:
        # Create and run test
        test = NI6535LoopbackTest(device_name=args.device)
        success = test.run_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}", file=sys.stderr)
        print("\nPlease ensure:")
        print("  1. NI-DAQmx drivers are installed")
        print("  2. The device is properly connected")
        print("  3. The device name is correct")
        print("  4. Hardware loopback connections are in place", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
