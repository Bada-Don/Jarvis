import psutil
import uiautomation as auto


def list_processes():
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            procs.append((p.info["pid"], p.info["name"]))
        except:
            pass
    return procs


def pick_process(procs):
    for i, (pid, name) in enumerate(procs):
        print(f"{i}: {name} (PID {pid})")
    idx = int(input("Select index: "))
    return procs[idx][0]


def dump_elements(element, depth=0):
    name = element.Name
    cls = element.ClassName
    aid = element.AutomationId
    ctrl_type = element.ControlTypeName

    print("  " * depth + f"- Name: {name}, Class: {cls}, AutomationId: {aid}, Type: {ctrl_type}")

    for child in element.GetChildren():
        dump_elements(child, depth + 1)


def main():
    procs = list_processes()
    pid = pick_process(procs)

    # Find the main window for the process
    root = auto.GetRootControl()
    
    # Search for windows belonging to this PID
    windows = []
    for win in root.GetChildren():
        try:
            if win.ProcessId == pid:
                windows.append(win)
        except:
            pass

    if not windows:
        print(f"No UI elements found for PID {pid}")
        return

    print(f"\nFound {len(windows)} top-level window(s) for PID {pid}\n")
    
    for win in windows:
        print(f"=== Window: {win.Name} ===")
        dump_elements(win)
        print()


if __name__ == "__main__":
    main()
