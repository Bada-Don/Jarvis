import { Moon, Sun, Laptop } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { useState, useRef, useEffect } from "react";

export function ThemeToggle() {
  const { setTheme, theme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary p-2 h-9 w-9 rounded-full"
        title="Toggle theme"
      >
        <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        <span className="sr-only">Toggle theme</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-36 rounded-md border border-border bg-popover p-1 shadow-l animate-fade-in z-50">
          <button
            onClick={() => {
              setTheme("light");
              setIsOpen(false);
            }}
            className={`flex w-full gap-2 items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground ${
              theme === "light" ? "bg-accent text-accent-foreground" : "text-popover-foreground"
            }`}
          >
            <Sun className="mr-2 h-4 w-4" />
            <span>Light</span>
          </button>
          <button
            onClick={() => {
              setTheme("dark");
              setIsOpen(false);
            }}
            className={`flex w-full items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground ${
              theme === "dark" ? "bg-accent text-accent-foreground" : "text-popover-foreground"
            }`}
          >
            <Moon className="mr-2 h-4 w-4" />
            <span>Dark</span>
          </button>
          <button
            onClick={() => {
              setTheme("system");
              setIsOpen(false);
            }}
            className={`flex w-full items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground ${
              theme === "system" ? "bg-accent text-accent-foreground" : "text-popover-foreground"
            }`}
          >
            <Laptop className="mr-2 h-4 w-4" />
            <span>System</span>
          </button>
        </div>
      )}
    </div>
  );
}
