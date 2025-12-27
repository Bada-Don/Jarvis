import os

print("🔍 Debugging Windows paths:")
print(f"User home: {os.path.expanduser('~')}")
print(f"Desktop path: {os.path.join(os.path.expanduser('~'), 'Desktop')}")
print(f"Desktop exists: {os.path.exists(os.path.join(os.path.expanduser('~'), 'Desktop'))}")

# Check if folders F1 and F2 exist
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
f1_path = os.path.join(desktop, "F1")
f2_path = os.path.join(desktop, "F2")

print(f"\nF1 folder: {f1_path}")
print(f"F1 exists: {os.path.exists(f1_path)}")
print(f"F2 folder: {f2_path}")
print(f"F2 exists: {os.path.exists(f2_path)}")

# List desktop contents
if os.path.exists(desktop):
    print(f"\nDesktop contents:")
    for item in os.listdir(desktop):
        item_path = os.path.join(desktop, item)
        item_type = "📁" if os.path.isdir(item_path) else "📄"
        print(f"  {item_type} {item}")
else:
    print("❌ Desktop path doesn't exist!")