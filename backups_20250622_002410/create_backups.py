import os
import shutil
from datetime import datetime

def create_backups():
    """Create backups of all HTML and Python files in the current directory"""
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Get current directory
    current_dir = "."
    
    # File extensions to backup
    extensions = ['.html', '.py']
    
    backed_up_files = []
    
    # Find and backup files
    for filename in os.listdir(current_dir):
        if any(filename.endswith(ext) for ext in extensions):
            src_path = os.path.join(current_dir, filename)
            dst_path = os.path.join(backup_dir, filename)
            
            try:
                shutil.copy2(src_path, dst_path)
                backed_up_files.append(filename)
                print(f"✓ Backed up: {filename}")
            except Exception as e:
                print(f"✗ Failed to backup {filename}: {e}")
    
    print(f"\nBackup completed! {len(backed_up_files)} files backed up to: {backup_dir}")
    print("Backed up files:")
    for file in sorted(backed_up_files):
        print(f"  - {file}")
    
    return backup_dir, backed_up_files

if __name__ == "__main__":
    create_backups()
