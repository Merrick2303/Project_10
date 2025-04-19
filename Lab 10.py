import asyncio
import shelve
from time import strftime, gmtime, sleep
from bleak import BleakScanner
import threading

# List of known devices (replace with your class list)
KNOWN_DEVICES = {
    "JBL Tune 520BT-LE-1": "2E4C301A-FF8F-692F-E945-01D27DBCD839",
    "JBL Tune 520BT-LE-2": "63971F11-682D-CF9F-6927-B40D1461895F"
}

# Scans for all Bluetooth devices (not used in final version, but useful for testing)
async def scan_for_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}")
    return devices

# Checks if any known device is nearby
async def check_for_known_devices():
    devices = await BleakScanner.discover()
    nearby_known_devices = {}

    for device in devices:
        if device.address in KNOWN_DEVICES.values():
            device_name = [name for name, addr in KNOWN_DEVICES.items() if addr == device.address][0]
            print(f"{device_name} is nearby!")
            nearby_known_devices[device_name] = device.address

    return nearby_known_devices

# Logs detected devices with timestamps into a shelf database
def log_devices(devices):
    with shelve.open("device_log") as db:
        for name, address in devices.items():
            key = name + '_' + address
            formatted_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            if key in db:
                time_list = db[key]
                time_list.append(formatted_time)
                db[key] = time_list
            else:
                db[key] = [formatted_time]
    print("Logged devices in the shelf database.")

# Async wrapper to scan and log
async def scan():
    nearby_devices = await check_for_known_devices()
    if nearby_devices:
        log_devices(nearby_devices)
    else:
        print("No known devices nearby.")

# Optional cleanup function to clear logs every hour
async def clear_logs_every_hour():
    while True:
        await asyncio.sleep(3600)  # Sleep for one hour
        with shelve.open("device_log") as db:
            db.clear()
        print("Cleared the device log.")

# Run continuous scanning and optionally log verification
def main():
    def run_log_cleaner():
        asyncio.run(clear_logs_every_hour())

    # Start log cleanup in a separate thread
    threading.Thread(target=run_log_cleaner, daemon=True).start()

    while True:
        print("Scanning...")
        asyncio.run(scan())
        print("Sleeping till next loop...")
        sleep(15)
        print("Verifying log...")
        with shelve.open("device_log") as db:
            for name, timestamps in db.items():
                print(f"{name}: {timestamps}")

if __name__ == '__main__':
    main()
