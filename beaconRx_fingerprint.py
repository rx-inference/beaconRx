# beaconRx_fingerprint.py
# PURPOSE: retrieves comprehensive system hardware configuration

import hashlib
import platform
import psutil
import subprocess
import argparse
import sys
import re

def get_cpu_info():
    """retrieves cpu model and core count"""
    return {
        "model": platform.processor(),
        "cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True)
    }

def get_gpu_info():
    """retrieves gpu information using system commands"""
    try:
        result = subprocess.check_output(
            "wmic path win32_VideoController get name",
            shell=True
        ).decode().strip()
        gpus = [line for line in result.split('\n') if line.strip()]
        return gpus[1:] if len(gpus) > 1 else ["No GPU detected"]
    except Exception:
        return ["GPU detection failed"]

def get_ram_info():
    """retrieves detailed RAM information"""
    try:
        # Get RAM modules with manufacturer and part number
        result = subprocess.check_output(
            "wmic memorychip get manufacturer,partnumber",
            shell=True
        ).decode().strip().split('\n')

        modules = []
        # Skip header and process each RAM module
        for line in result[1:]:
            if not line.strip(): continue
            # Split only on the first space to preserve part numbers with spaces
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                modules.append(line.strip())
            else:
                modules.append(f"{parts[0]} {parts[1]}")

        # Get total RAM separately
        mem = psutil.virtual_memory()
        total_ram = round(mem.total / (1024 ** 3), 1)

        return {
            "modules": modules,
            "total_gb": total_ram
        }
    except Exception:
        return {
            "modules": ["RAM details detection failed"],
            "total_gb": 0
        }

def get_storage_info():
    """gets disk drive information"""
    partitions = psutil.disk_partitions()
    storage = []
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            storage.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "total_gb": round(usage.total / (1024**3), 1)
            })
        except Exception:
            continue
    return storage

def get_motherboard_info():
    """retrieves motherboard and BIOS information"""
    try:
        # Get motherboard information
        baseboard = subprocess.check_output(
            "wmic baseboard get product,Manufacturer,version",
            shell=True
        ).decode().strip().split('\n')[1].split()

        # Get BIOS information
        bios = subprocess.check_output(
            "wmic bios get serialnumber,version,manufacturer",
            shell=True
        ).decode().strip().split('\n')[1].split()

        return {
            "motherboard": f"{baseboard[0]} {baseboard[1]} (v{baseboard[2]})",
            "bios": f"{bios[0]} {bios[1]} (SN: {bios[2]})"
        }
    except Exception:
        return {
            "motherboard": "Unknown",
            "bios": "Unknown"
        }

def get_display_info():
    """retrieves connected display types"""
    try:
        result = subprocess.check_output(
            "wmic path Win32_DesktopMonitor get Name",
            shell=True
        ).decode().strip().split('\n')
        # Skip header line and filter empty lines
        displays = [line.strip() for line in result[1:] if line.strip()]
        return displays if displays else ["No displays detected"]
    except Exception:
        return ["Display detection failed"]

def generate_hardware_string(username, passkey):
    """creates compact hardware string without spaces"""
    components = []

    # Add username and passkey to the hardware string
    components.append(username)
    components.append(passkey)

    # CPU info
    cpu = get_cpu_info()
    components.append(f"{cpu['model'].replace(' ', '')}")
    components.append(f"P{cpu['cores']}L{cpu['logical_cores']}")  # Physical and logical cores

    # GPU info
    gpus = get_gpu_info()
    for gpu in gpus:
        components.append(gpu.replace(' ', ''))

    # RAM info
    ram_info = get_ram_info()
    for module in ram_info['modules']:
        components.append(module.replace(' ', ''))
    components.append(f"T{ram_info['total_gb']}GB")

    # Storage info
    storage = get_storage_info()
    for disk in storage:
        components.append(disk['device'].replace(' ', ''))
        components.append(disk['fstype'].replace(' ', ''))
        components.append(f"{disk['total_gb']}GB")

    # Motherboard/BIOS
    mobo = get_motherboard_info()
    components.append(mobo['motherboard'].replace(' ', ''))
    components.append(mobo['bios'].replace(' ', ''))

    # Display info
    displays = get_display_info()
    for display in displays:
        components.append(display.replace(' ', ''))

    return ''.join(components)

def secure_fingerprint(hardware_string, username, passkey):
    """applies secure hashing to hardware string"""
    results = {}

    # PBKDF2 key stretching with 100,000 iterations
    pbkdf2_hash = hashlib.pbkdf2_hmac(
        'sha256',
        hardware_string.encode(),
        (username + passkey).encode(),  # Using username and passkey as salt
        100000
    ).hex()
    results['pbkdf2_hash'] = pbkdf2_hash

    return results

def sanitize_input(value, field_name):
    """sanitizes input to allow only alphanumeric characters"""
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        print("Error: Only 0-9, a-z, A-Z are allowed in usernames and passkeys.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    return value

if __name__ == "__main__":
    # Custom help message
    help_message = """
beaconRx_fingerprint v.0.0.4 - Rx Hardware Fingerprint Generator

Usage:
  beaconRx_fingerprint.py --username USERNAME --passkey PASSKEY

Options:
  --help, -h          Show this help message and exit.
  --username, -u      Preferred username (0-9, a-z, A-Z)
  --passkey, -p       Preferred passkey (0-9, a-z, A-Z)
 
Examples:
  python beaconRx_fingerprint.py --username john --passkey mypass123
  python beaconRx_fingerprint.py -u alice -p secretkey
"""

    # Check for help first
    if '--help' in sys.argv or '-h' in sys.argv:
        print(help_message)
        sys.exit(0)
    
    # Check if no arguments
    if len(sys.argv) == 1:
        print("Error: Username and passkey are required.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    
    # Check for duplicate arguments
    username_count = sys.argv.count('-u') + sys.argv.count('--username')
    passkey_count = sys.argv.count('-p') + sys.argv.count('--passkey')
    
    if username_count > 1 or passkey_count > 1:
        print("Error: Invalid input.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    
    # Check for missing values after -u or -p
    args_list = sys.argv[1:]
    for i, arg in enumerate(args_list):
        if arg in ['-u', '--username']:
            if i + 1 >= len(args_list) or args_list[i + 1].startswith('-'):
                print("Error: Username missing.")
                print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
                print("Use --help for more information.")
                sys.exit(1)
        elif arg in ['-p', '--passkey']:
            if i + 1 >= len(args_list) or args_list[i + 1].startswith('-'):
                print("Error: Passkey missing.")
                print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
                print("Use --help for more information.")
                sys.exit(1)
    
    # Check for specific missing arguments
    has_username = any(arg in ['--username', '-u'] for arg in sys.argv)
    has_passkey = any(arg in ['--passkey', '-p'] for arg in sys.argv)
    
    if not has_username and has_passkey:
        print("Error: Username missing.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    
    if has_username and not has_passkey:
        print("Error: Passkey missing.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    
    # Check for unrecognized arguments
    valid_args = ['--username', '-u', '--passkey', '-p', '--help', '-h']
    for arg in sys.argv[1:]:
        if arg.startswith('-') and arg not in valid_args:
            print("Error: Invalid input.")
            print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
            print("Use --help for more information.")
            sys.exit(1)
    
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    parser.add_argument('--username', '-u', required=True, help=argparse.SUPPRESS)
    parser.add_argument('--passkey', '-p', required=True, help=argparse.SUPPRESS)
    
    try:
        args = parser.parse_args()
    except:
        print("Error: Invalid input.")
        print("Usage: beaconRx_fingerprint.py -u USERNAME -p PASSKEY")
        print("Use --help for more information.")
        sys.exit(1)
    
    # Sanitize inputs
    username = sanitize_input(args.username, "Username")
    passkey = sanitize_input(args.passkey, "Passkey")

    print()
    print("beaconRx_fingerprint v.0.0.4 - Rx Hardware Fingerprint Generator")
    print()
    print()

    print("=== SYSTEM HARDWARE CONFIGURATION ===")
    print()

    cpu = get_cpu_info()
    print(f"CPU: {cpu['model']}")
    print(f"Physical cores: {cpu['cores']}")
    print(f"Logical cores: {cpu['logical_cores']}")

    gpus = get_gpu_info()
    print("\nGPU(s):")
    for i, gpu in enumerate(gpus, 1):
        print(f"{i}. {gpu}")

    displays = get_display_info()
    print("\nDISPLAYS:")
    for i, display in enumerate(displays, 1):
        print(f"{i}. {display}")

    ram_info = get_ram_info()
    print("\nRAM MODULES:")
    if ram_info["modules"]:
        for i, module in enumerate(ram_info["modules"], 1):
            print(f"{i}. {module}")
    print(f"\nTOTAL RAM: {ram_info['total_gb']} GB")

    storage = get_storage_info()
    print("\nSTORAGE:")
    for disk in storage:
        print(f"{disk['device']} ({disk['fstype']}): {disk['total_gb']} GB")

    mobo = get_motherboard_info()
    print("\nMOTHERBOARD & BIOS:")
    print(f"Board: {mobo['motherboard']}")
    print(f"BIOS: {mobo['bios']}")
    print()
    print()

    # Generate compact hardware string
    hardware_string = generate_hardware_string(username, passkey)
    print("=== COMPACT HARDWARE STRING ===")
    print()
    print(hardware_string)
    print()

    # Apply secure fingerprinting
    result = secure_fingerprint(hardware_string, username, passkey)

    print("=== SECURE FINGERPRINT ===")
    print()
    print("PBKDF2 Hash (100,000 iterations):")
    print(result['pbkdf2_hash'])
    print()