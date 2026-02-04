# NI PCIe-6535 Loopback Test

This Python program tests the port read functionality of the NI PCIe-6535 digital I/O board by performing loopback tests between ports 0 & 2 and 1 & 3.

![Loopback Wiring](images/loopback_test_wiring.jpg)

## Hardware Setup

Before running the test, connect the following ports with appropriate wiring:
- **Port 0 to Port 2** (all 8 channels: DIO0-DIO7 to DIO16-DIO23)
- **Port 1 to Port 3** (all 8 channels: DIO8-DIO15 to DIO24-DIO31)

## Installation

1. Install NI-DAQmx drivers from National Instruments
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the loopback test with the default device (Dev1):
```bash
python loopback_test.py
```

Run with a specific device name:
```bash
python loopback_test.py --device Dev2
```

## Test Description

The program performs comprehensive loopback testing:

1. **Port 0 → Port 2**: Write test patterns to Port 0, read from Port 2
2. **Port 2 → Port 0**: Write test patterns to Port 2, read from Port 0
3. **Port 1 → Port 3**: Write test patterns to Port 1, read from Port 3
4. **Port 3 → Port 1**: Write test patterns to Port 3, read from Port 1

### Test Patterns

Each port pair is tested with the following patterns:
- All zeros (0x00)
- All ones (0xFF)
- Alternating bits (0xAA, 0x55)
- Walking 1s (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)
- Walking 0s (0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F)
- Additional patterns (0x0F, 0xF0, 0x33, 0xCC)

This ensures all 8 channels on each port are thoroughly tested.

## Output

The program displays:
- Test progress for each pattern
- Pass/Fail status for each test
- Summary with total tests, passed, failed, and success rate
- Detailed listing of any failed tests

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed
- `2`: Fatal error (e.g., device not found, NI-DAQmx not installed)
