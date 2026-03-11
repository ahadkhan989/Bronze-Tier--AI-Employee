"""
File System Watcher Module

Monitors a drop folder for new files and creates action files in the Obsidian vault.
This is the simplest watcher to set up - just drop files into the monitored folder.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Optional watchdog import for efficient file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Note: watchdog not installed. Using polling mode instead.")
    print("Install with: pip install watchdog")


class FileDropHandler(FileSystemEventHandler):
    """
    Handles file system events for the drop folder.
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        self.logger.info(f'File detected: {event.src_path}')
        self.watcher.process_file(Path(event.src_path))


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    When a file is dropped:
    1. Copy file to vault's Inbox folder
    2. Create metadata .md file in Needs_Action
    3. Log the action
    
    Attributes:
        drop_folder: Path to the folder being monitored
        processed_hashes: Set of file hashes already processed
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            drop_folder: Path to the folder to monitor (default: vault/Inbox/Drop)
            check_interval: How often to check for updates (in seconds)
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.inbox / 'Drop'
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_hashes: set = set()
        
        # File type handlers
        self.file_handlers = {
            '.txt': self._handle_text_file,
            '.md': self._handle_markdown_file,
            '.pdf': self._handle_document_file,
            '.doc': self._handle_document_file,
            '.docx': self._handle_document_file,
            '.jpg': self._handle_image_file,
            '.jpeg': self._handle_image_file,
            '.png': self._handle_image_file,
            '.csv': self._handle_data_file,
            '.json': self._handle_data_file,
            '.xlsx': self._handle_data_file,
        }
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _handle_text_file(self, filepath: Path) -> str:
        """Extract preview from text file."""
        try:
            content = filepath.read_text(encoding='utf-8')[:500]
            return content.replace('\n', ' ')
        except:
            return "Text file (content not previewable)"
    
    def _handle_markdown_file(self, filepath: Path) -> str:
        """Extract preview from markdown file."""
        return self._handle_text_file(filepath)
    
    def _handle_document_file(self, filepath: Path) -> str:
        """Handle document files."""
        return f"Document: {filepath.name}"
    
    def _handle_image_file(self, filepath: Path) -> str:
        """Handle image files."""
        return f"Image: {filepath.name}"
    
    def _handle_data_file(self, filepath: Path) -> str:
        """Handle data files (CSV, JSON, Excel)."""
        return f"Data file: {filepath.name}"
    
    def process_file(self, filepath: Path):
        """
        Process a newly detected file (used by watchdog mode).

        Args:
            filepath: Path to the detected file
        """
        try:
            # Calculate hash to check for duplicates
            file_hash = self._get_file_hash(filepath)

            if file_hash in self.processed_hashes:
                self.logger.debug(f'File already processed (hash match): {filepath.name}')
                return

            # Copy file to inbox
            dest = self.inbox / filepath.name
            shutil.copy2(filepath, dest)
            self.logger.info(f'Copied file to inbox: {dest.name}')

            # Create action file (this will also delete from drop folder)
            self.create_action_file({
                'source_path': filepath,
                'dest_path': dest,
                'filename': filepath.name,
                'size': filepath.stat().st_size,
                'hash': file_hash
            })

        except Exception as e:
            self.logger.error(f'Error processing file {filepath}: {e}')
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of file info dictionaries for new files
        """
        new_files = []
        
        try:
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file():
                    file_hash = self._get_file_hash(filepath)
                    if file_hash not in self.processed_hashes:
                        new_files.append({
                            'source_path': filepath,
                            'dest_path': self.inbox / filepath.name,
                            'filename': filepath.name,
                            'size': filepath.stat().st_size,
                            'hash': file_hash
                        })
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: Dictionary containing file information
            
        Returns:
            Path to the created file, or None if creation failed
        """
        try:
            filename = self.sanitize_filename(item['filename'])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            action_filename = f"FILE_{timestamp}_{filename}.md"
            filepath = self.needs_action / action_filename
            
            # Get file type description
            file_ext = Path(item['filename']).suffix.lower()
            handler = self.file_handlers.get(file_ext, lambda x: f"File: {x['filename']}")
            description = handler(item)
            
            content = f"""---
type: file_drop
source: filesystem_watcher
filename: {filename}
original_path: {item['source_path']}
vault_path: {item['dest_path']}
size: {item['size']} bytes
file_hash: {item['hash']}
received: {self.get_timestamp()}
priority: normal
status: pending
---

# File Drop: {filename}

## File Information
- **Size:** {item['size']} bytes
- **Type:** {file_ext or 'Unknown'}
- **Received:** {self.get_timestamp()}
- **Location:** `{item['dest_path']}`

## Description
{description}

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file type
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
*Add notes here during processing*

---
*Created by FileSystemWatcher*
"""
            
            filepath.write_text(content, encoding='utf-8')
            
            # Mark hash as processed to prevent duplicates
            self.processed_hashes.add(item['hash'])
            
            # Delete the file from drop folder to prevent re-processing
            source_path = item['source_path']
            if isinstance(source_path, Path) and source_path.exists():
                source_path.unlink()
                self.logger.info(f'Removed from drop folder: {item["filename"]}')
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def run_with_watchdog(self):
        """
        Run using watchdog for efficient file monitoring.
        Falls back to polling if watchdog is not available.
        """
        if not WATCHDOG_AVAILABLE:
            self.logger.info('Watchdog not available, using polling mode')
            self.run()
            return
        
        self.logger.info(f'Starting {self.__class__.__name__} (watchdog mode)')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        try:
            handler = FileDropHandler(self)
            observer = Observer()
            observer.schedule(handler, str(self.drop_folder), recursive=False)
            observer.start()
            self.logger.info('Watching for files...')
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            observer.stop()
            raise
        finally:
            observer.join()


def main():
    """Main entry point for the filesystem watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault directory')
    parser.add_argument('--drop-folder', '-d', help='Path to the drop folder to monitor')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Check interval in seconds')
    parser.add_argument('--watchdog', '-w', action='store_true', help='Use watchdog (if available)')
    
    args = parser.parse_args()
    
    watcher = FileSystemWatcher(
        vault_path=args.vault_path,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    
    if args.watchdog and WATCHDOG_AVAILABLE:
        watcher.run_with_watchdog()
    else:
        watcher.run()


if __name__ == '__main__':
    main()
