import sys
from src.observer import run_checks


DATA_PATH = "data/students.csv"


def main() -> None:
    print("Running Pipeline Health Observer...\n")

    results = run_checks(DATA_PATH)

    failed = False
    for result in results:
        icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(result["status"], "❓")
        print(f"{icon}  [{result['status']}] {result['check']}: {result['details']}")
        if result["status"] == "FAIL":
            failed = True

    print()
    if failed:
        print("One or more checks FAILED. Review the issues above.")
        sys.exit(1)
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
