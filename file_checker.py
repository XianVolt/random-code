import os

def check_path(path):
    """Check whether a file or folder exists."""
    if not os.path.exists(path):
        print("\n[NOT FOUND] The file or folder does not exist.")
        return

    if os.path.isfile(path):
        size = os.path.getsize(path)
        print("\n[AVAILABLE] File found!")
        print(f"Name: {os.path.basename(path)}")
        print(f"Size: {size:,} bytes")
    elif os.path.isdir(path):
        print("\n[AVAILABLE] Folder found!")
        print(f"Name: {os.path.basename(os.path.abspath(path)) or path}")

def main():
    print("=" * 34)
    print("         PYTHON FILE CHECKER")
    print("=" * 34)
    path = input("Enter a file or folder path: ").strip().strip('"')

    if not path:
        print("\nPlease enter a path.")
        return

    check_path(path)
    print("\nDone.")

if __name__ == "__main__":
    main()
