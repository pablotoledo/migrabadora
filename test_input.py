import sounddevice as sd
import numpy as np

def test_device(device_index):
    try:
        print(f"Testing device {device_index}...")
        device_info = sd.query_devices(device_index)
        print(f"Name: {device_info['name']}")
        print(f"Inputs: {device_info['max_input_channels']}")
        
        # Try to open an input stream
        with sd.InputStream(device=device_index, channels=1, samplerate=44100) as stream:
            print("Successfully opened input stream!")
            data, overflowed = stream.read(44100) # Read 1 second
            print(f"Read {len(data)} frames")
            
    except Exception as e:
        print(f"FAILED to open input stream: {e}")

# Test the Multi-Output Device (index 5 based on previous output)
# Note: Index might change, looking for name match
found = False
for idx, dev in enumerate(sd.query_devices()):
    if "salida múltiple" in dev['name'].lower() or "multi-output" in dev['name'].lower():
        test_device(idx)
        found = True

if not found:
    print("Multi-Output device not found in list")
