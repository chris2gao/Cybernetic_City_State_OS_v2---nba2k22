import os
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CQRS_Projector")

class CQRSProjector:
    def __init__(self, jsonl_path, md_path):
        self.jsonl_path = jsonl_path
        self.md_path = md_path
        self.temp_md_path = md_path + ".temp"
        
        self.last_offset = 0
        self.last_size = -1
        self.last_mtime = -1
        
        self.consecutive_errors = 0
        self.downgraded = False
        
        self.state = {
            "last_updated": None,
            "issue_id": None,
            "events": []
        }

    def _atomic_write(self, content):
        """Writes content to md_path atomically with PermissionError fallback."""
        with open(self.temp_md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        retries = 3
        delay = 0.1
        for i in range(retries):
            try:
                os.replace(self.temp_md_path, self.md_path)
                return True
            except PermissionError as e:
                logger.warning(f"PermissionError on replace: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        
        logger.error(f"Failed to atomically write {self.md_path} after {retries} retries.")
        return False

    def _render_state(self):
        """Renders the in-memory state dictionary to a flat Markdown string."""
        lines = []
        lines.append(f"# 赛博城邦状态视图 (Status View)")
        lines.append(f"**Last Updated**: {self.state['last_updated'] or 'Never'}")
        lines.append(f"**Issue ID**: {self.state['issue_id'] or 'Unknown'}")
        if self.downgraded:
            lines.append("\n> [!CAUTION]")
            lines.append("> **系统降级中**: 连续检测到脏数据，当前视图为最后的健康快照，新事件已暂停同步。")
            
        lines.append("\n## 事件流水 (Event Stream)\n")
        
        for idx, event in enumerate(self.state['events'], 1):
            lines.append(f"### [{idx}] {event['timestamp']} - {event['agent_role']} ({event['action_type']})")
            lines.append(f"{event['content']}\n")
            lines.append("---\n")
            
        return "\n".join(lines)

    def _process_new_lines(self):
        """Reads new lines from the jsonl file, parses them, and updates state."""
        if self.downgraded:
            return False # Skip processing if downgraded
            
        new_events = False
        try:
            with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                f.seek(self.last_offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        self.consecutive_errors = 0 # reset counter
                        
                        # Structural checks
                        if 'schema_version' not in data or 'action_type' not in data:
                            logger.critical(f"Structural Break: Missing core fields in event: {data}")
                            raise RuntimeError(f"Structural Integrity Compromised: {data}")
                        
                        self.state['last_updated'] = data.get('timestamp', '')
                        self.state['issue_id'] = data.get('issue_id', self.state['issue_id'])
                        self.state['events'].append({
                            'timestamp': data.get('timestamp', ''),
                            'agent_role': data.get('agent_role', 'UNKNOWN'),
                            'action_type': data.get('action_type', 'UNKNOWN'),
                            'content': data.get('content', '')
                        })
                        new_events = True
                        
                    except json.JSONDecodeError as e:
                        self.consecutive_errors += 1
                        logger.warning(f"Dirty Data detected (JSONDecodeError): {e}. Skipping line. Consecutive errors: {self.consecutive_errors}")
                        if self.consecutive_errors >= 5:
                            logger.error("Consecutive error limit reached. Initiating Tiered Downgrade.")
                            self.downgraded = True
                            return True # Force render to show downgrade warning
                            
                self.last_offset = f.tell()
        except FileNotFoundError:
            pass # File doesn't exist yet, that's fine
            
        return new_events

    def run(self, max_iterations=None):
        """Main adaptive polling loop."""
        logger.info(f"Starting CQRS Projector. Watching {self.jsonl_path} -> {self.md_path}")
        idle_sleep = 0.1
        max_idle_sleep = 2.0
        active_sleep = 0.05
        
        iterations = 0
        
        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break
            iterations += 1
            
            try:
                st = os.stat(self.jsonl_path)
                current_size = st.st_size
                current_mtime = st.st_mtime
            except FileNotFoundError:
                current_size = -1
                current_mtime = -1
                
            if current_size != self.last_size or current_mtime != self.last_mtime:
                # File changed
                self.last_size = current_size
                self.last_mtime = current_mtime
                
                logger.info("File change detected. Processing...")
                changed = self.process_once()
                
                if changed:
                    idle_sleep = 0.1 # reset backoff
                    time.sleep(active_sleep)
                else:
                    # Could just be mtime change without new valid data
                    pass
            else:
                # No change, exponential backoff
                time.sleep(idle_sleep)
                idle_sleep = min(idle_sleep * 1.5, max_idle_sleep)
                
    def process_once(self):
        """Processes the file once. Useful for testing."""
        changed = self._process_new_lines()
        if changed:
            md_content = self._render_state()
            self._atomic_write(md_content)
        return changed

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="V6 CQRS Projector")
    parser.add_argument("--jsonl", default="../03_Daily_Execution/activity.jsonl", help="Input event stream")
    parser.add_argument("--md", default="../03_Daily_Execution/status.md", help="Output materialized view")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for testing)")
    
    args = parser.parse_args()
    
    projector = CQRSProjector(args.jsonl, args.md)
    if args.once:
        projector.process_once()
    else:
        projector.run()
