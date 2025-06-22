import os
import shutil
import glob

def list_backups():
    """List all available backup directories"""
    backup_dirs = glob.glob("backups_*")
    backup_dirs.sort(reverse=True)  # Most recent first
    return backup_dirs

def restore_from_backup(backup_dir, files_to_restore=None):
    """Restore files from a backup directory
    
    Args:
        backup_dir: The backup directory to restore from
        files_to_restore: List of specific files to restore, or None for all files
    """
    if not os.path.exists(backup_dir):
        print(f"Backup directory {backup_dir} does not exist!")
        return False
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith(('.html', '.py'))]
    
    if files_to_restore is None:
        files_to_restore = backup_files
    
    restored_files = []
    
    for filename in files_to_restore:
        if filename not in backup_files:
            print(f"✗ File {filename} not found in backup")
            continue
            
        src_path = os.path.join(backup_dir, filename)
        dst_path = filename
        
        try:
            shutil.copy2(src_path, dst_path)
            restored_files.append(filename)
            print(f"✓ Restored: {filename}")
        except Exception as e:
            print(f"✗ Failed to restore {filename}: {e}")
    
    print(f"\nRestore completed! {len(restored_files)} files restored.")
    return True

def main():
    """Interactive restore utility"""
    backups = list_backups()
    
    if not backups:
        print("No backup directories found!")
        return
    
    print("Available backups:")
    for i, backup in enumerate(backups):
        print(f"  {i+1}. {backup}")
    
    try:
        choice = int(input(f"\nSelect backup to restore from (1-{len(backups)}): ")) - 1
        if 0 <= choice < len(backups):
            selected_backup = backups[choice]
            
            # Show files in selected backup
            backup_files = [f for f in os.listdir(selected_backup) if f.endswith(('.html', '.py'))]
            print(f"\nFiles in {selected_backup}:")
            for file in sorted(backup_files):
                print(f"  - {file}")
            
            confirm = input(f"\nRestore all files from {selected_backup}? (y/N): ")
            if confirm.lower() == 'y':
                restore_from_backup(selected_backup)
            else:
                print("Restore cancelled.")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\nRestore cancelled.")

if __name__ == "__main__":
    main()
