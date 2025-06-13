# beaconRx_fingerprint.py
# PURPOSE: retrieves comprehensive system hardware configuration

import hashlib
import platform
import psutil
import subprocess
import argparse

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

def secure_fingerprint_stages(hardware_string, username, passkey):
    """applies secure hashing to hardware string"""
    results = {}

    # 1. SHA-256 hashing
    salted_hardware_string = f"{username}{hardware_string}{passkey}"
    hash1 = hashlib.sha256(salted_hardware_string.encode()).hexdigest()
    results['sha256_hash'] = hash1

    # 2. PBKDF2 key stretching with 100,000 iterations
    pbkdf2_hash = hashlib.pbkdf2_hmac(
        'sha256',
        hash1.encode(),
        (username + passkey).encode(),  # Using username and passkey as salt
        100000
    ).hex()
    results['pbkdf2_hash'] = pbkdf2_hash

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate hardware fingerprint')
    parser.add_argument('--username', required=True, help='Username for salting')
    parser.add_argument('--passkey', required=True, help='Passkey for salting')
    args = parser.parse_args()

    print("=== SYSTEM HARDWARE CONFIGURATION ===")

    cpu = get_cpu_info()
    print(f"\nCPU: {cpu['model']}")
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

    # Generate compact hardware string
    hardware_string = generate_hardware_string(args.username, args.passkey)
    print("\nCOMPACT HARDWARE STRING:")
    print(hardware_string)

    # Apply secure fingerprinting stages
    stages = secure_fingerprint_stages(hardware_string, args.username, args.passkey)

    print("\nSECURE FINGERPRINTING STAGES:")
    print("1. SHA-256 Hash:")
    print(stages['sha256_hash'])

    print("\n2. PBKDF2 Hash (100,000 iterations):")
    print(stages['pbkdf2_hash'])