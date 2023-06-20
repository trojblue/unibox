import subprocess
import re


def setup_swap(size: str):
    size_match = re.match(r'(\d+)([GMK])', size.upper())
    if not size_match:
        raise ValueError("Invalid size. Use standard notation, e.g., 1G, 1024M, 1048576K.")
    size_val, size_unit = size_match.groups()
    size_val = int(size_val)

    if size_unit == 'M':
        size_val //= 1024
    elif size_unit == 'K':
        size_val //= (1024 * 1024)

    # Disable existing swap
    subprocess.run(['sudo', 'swapoff', '/swapfile'], check=True)

    # Create new swap file with specified size
    subprocess.run(['sudo', 'dd', 'if=/dev/zero', f'of=/swapfile', f'bs=1G', f'count={size_val}'], check=True)

    # Secure the swap file
    subprocess.run(['sudo', 'chmod', '600', '/swapfile'], check=True)

    # Set up the swap area
    subprocess.run(['sudo', 'mkswap', '/swapfile'], check=True)

    # Enable the swap file
    subprocess.run(['sudo', 'swapon', '/swapfile'], check=True)

    # Show the swap details
    subprocess.run(['sudo', 'swapon', '--show'], check=True)


def setup_linux():
    print("setup linux in setups.py")
    pass

def setup_awscli():
    print("install awscli")
    pass

