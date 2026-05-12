"""
Batch Processing Conductor
Manages parallel job processing with ThreadPoolExecutor, file-based locks,
retry logic, and resumable state tracking.
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional
from datetime import datetime
from pathlib import Path
import hashlib


class BatchConductor:
    """Manages batch job processing with parallel workers"""

    def __init__(self, max_workers: int = 8, state_file: str = None):
        self.max_workers = max_workers
        self.state_file = state_file or str(
            Path(__file__).parent.parent / "data" / "batch_state.json"
        )
        self.lock_dir = Path(__file__).parent.parent / "data" / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)

        self.queue = []
        self.results = []
        self.failed = []
        self.is_running = False
        self.progress = {'total': 0, 'completed': 0, 'failed': 0, 'in_progress': 0, 'status': 'idle'}
        self._lock = threading.Lock()

    def process_queue(
        self,
        items: List[Dict],
        processor_fn: Callable[[Dict], Dict],
        progress_callback: Optional[Callable] = None,
        max_retries: int = 2
    ) -> List[Dict]:
        """Process all items with parallel workers"""
        self.is_running = True
        self.results = []
        self.failed = []
        self.progress = {'total': len(items), 'completed': 0, 'failed': 0, 'in_progress': 0, 'status': 'running'}

        # Prepare queue items with metadata
        queue_items = []
        for item in items:
            queue_items.append({
                'data': item,
                'retries': 0,
                'max_retries': max_retries,
                'status': 'pending'
            })

        print(f"\n[BatchConductor] Processing {len(queue_items)} items with {self.max_workers} workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for qi in queue_items:
                lock_key = self._get_lock_key(qi['data'])
                if not self._acquire_lock(lock_key):
                    print(f"  [SKIP] Lock held for: {lock_key}")
                    continue

                qi['status'] = 'in_progress'
                with self._lock:
                    self.progress['in_progress'] += 1

                future = executor.submit(self._process_item, processor_fn, qi, lock_key)
                futures[future] = qi

            for future in as_completed(futures):
                qi = futures[future]
                lock_key = self._get_lock_key(qi['data'])

                try:
                    result = future.result()
                    qi['status'] = 'completed'
                    self.results.append(result)
                    with self._lock:
                        self.progress['completed'] += 1
                        self.progress['in_progress'] -= 1
                except Exception as e:
                    qi['retries'] += 1
                    with self._lock:
                        self.progress['in_progress'] -= 1

                    if qi['retries'] < qi['max_retries']:
                        qi['status'] = 'pending'
                        # Retry
                        print(f"  [RETRY {qi['retries']}/{qi['max_retries']}] {e}")
                        try:
                            result = processor_fn(qi['data'])
                            qi['status'] = 'completed'
                            self.results.append(result)
                            with self._lock:
                                self.progress['completed'] += 1
                        except Exception as retry_err:
                            qi['status'] = 'failed'
                            qi['error'] = str(retry_err)
                            self.failed.append(qi)
                            with self._lock:
                                self.progress['failed'] += 1
                    else:
                        qi['status'] = 'failed'
                        qi['error'] = str(e)
                        self.failed.append(qi)
                        with self._lock:
                            self.progress['failed'] += 1

                self._release_lock(lock_key)

                # Update progress callback
                if progress_callback:
                    progress_callback(self.progress)

                # Save state periodically
                self._save_state()

        self.is_running = False
        self.progress['status'] = 'completed'
        self._save_state()
        self._cleanup_locks()

        print(f"[BatchConductor] Done: {self.progress['completed']} completed, {self.progress['failed']} failed")
        return self.results

    def _process_item(self, processor_fn: Callable, queue_item: Dict, lock_key: str) -> Dict:
        """Process a single item (runs in thread)"""
        return processor_fn(queue_item['data'])

    def _get_lock_key(self, item: Dict) -> str:
        """Generate a unique lock key for an item"""
        url = item.get('job_url', '') or item.get('url', '') or str(item.get('id', ''))
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _acquire_lock(self, key: str) -> bool:
        """File-based lock to prevent double execution (atomic)"""
        lock_file = self.lock_dir / f"{key}.lock"
        try:
            with open(lock_file, 'x') as f:
                f.write(datetime.now().isoformat())
            return True
        except FileExistsError:
            return False
        except Exception:
            return False

    def _release_lock(self, key: str):
        """Release a file-based lock"""
        lock_file = self.lock_dir / f"{key}.lock"
        try:
            lock_file.unlink(missing_ok=True)
        except:
            pass

    def _cleanup_locks(self):
        """Clean up all lock files"""
        try:
            for lock_file in self.lock_dir.glob("*.lock"):
                lock_file.unlink(missing_ok=True)
        except:
            pass

    def _save_state(self):
        """Save current state for crash recovery"""
        try:
            state = {
                'progress': self.progress,
                'failed_count': len(self.failed),
                'results_count': len(self.results),
                'saved_at': datetime.now().isoformat(),
            }
            Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"  [BatchConductor] State save error: {e}")

    def get_progress(self) -> Dict:
        """Get current progress"""
        return self.progress
