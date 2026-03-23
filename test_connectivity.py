import socket

# Test basic internet connectivity
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("✓ Internet connectivity: OK")
except OSError:
    print("✗ No internet connection - check your network")

# Test Google API access
try:
    socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=3)
    print("✓ Google API access: OK")
except OSError:
    print("✗ Cannot reach Google API - check firewall/proxy settings")
