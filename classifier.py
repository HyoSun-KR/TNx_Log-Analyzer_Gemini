"""
Log Data Classifier Module (Enhanced with In-depth Measurements)
- Extracts full metadata, execution parameters, and in-depth measurements from ptlog files
- Classifies into 4 hierarchical levels:
  1. Vendor (업체)
  2. Model (모델)
  3. Step (공정 단계)
  4. Pass / Fail (결과)
- Extracts numerical metrics: VDDA mV, Baseline Global Avg, Deviation %, Untouched Deltas Max/Min, Step Attempts & Durations
"""

import os
import shutil
import re
from datetime import datetime

class LogItem:
    def __init__(self, src_path):
        self.src_path = src_path
        self.file_name = os.path.basename(src_path)
        self.file_size = os.path.getsize(src_path)
        
        # Classification Hierarchies
        self.vendor = "Unknown_Vendor"
        self.model = "Unknown_Model"
        self.step = "Unknown_Step"
        self.result = "UNKNOWN"  # PASS or FAIL
        
        # Metadata
        self.test_date = "Unknown"
        self.test_time = "Unknown"
        self.barcode = "-"
        self.project = ""
        self.factory_id = ""
        self.test_type = ""
        self.test_name = ""
        self.test_revision = ""
        self.config_path = ""
        self.log_header_path = ""
        
        # Execution Metrics
        self.total_time_str = "00:00:00"
        self.total_time_sec = 0.0
        self.failed_substeps = []
        self.warning_substeps = []
        self.failure_reasons = []
        self.defect_category = "None"
        
        # In-depth Numerical Measurements
        self.vdda_mv = None
        self.baseline_avg = None
        self.baseline_dev = None
        self.delta_max = None
        self.delta_min = None
        self.step_details = {} # step_name -> {status: PASS/FAIL/WARN, attempts: N, time_sec: float}
        self.retry_count = 0
        self.is_retry_recovered = False
        
        # Additional Classification Categories
        self.screen_size_category = "Unknown" # Small (<=8"), Medium (10~13"), Large (>=15")
        self.defect_mechanism = "Normal"     # Baseline, Pin Leakage, Deltas Saturation, Timeout, Barcode, Normal
        self.test_stability = "Clean Pass"   # Clean Pass, Retry Recovered, Hard Fail
        
        # Destination
        self.dest_path = ""

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "src_path": self.src_path,
            "dest_path": self.dest_path,
            "file_size": self.file_size,
            "vendor": self.vendor,
            "model": self.model,
            "step": self.step,
            "result": self.result,
            "test_date": self.test_date,
            "test_time": self.test_time,
            "barcode": self.barcode,
            "project": self.project,
            "factory_id": self.factory_id,
            "test_type": self.test_type,
            "test_name": self.test_name,
            "test_revision": self.test_revision,
            "total_time_str": self.total_time_str,
            "total_time_sec": self.total_time_sec,
            "failed_substeps": self.failed_substeps,
            "warning_substeps": self.warning_substeps,
            "failure_reasons": self.failure_reasons,
            "defect_category": self.defect_category,
            "vdda_mv": self.vdda_mv,
            "baseline_avg": self.baseline_avg,
            "baseline_dev": self.baseline_dev,
            "delta_max": self.delta_max,
            "delta_min": self.delta_min,
            "step_details": self.step_details,
            "retry_count": self.retry_count,
            "is_retry_recovered": self.is_retry_recovered,
            "screen_size_category": self.screen_size_category,
            "defect_mechanism": self.defect_mechanism,
            "test_stability": self.test_stability,
        }


def parse_time_to_seconds(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
    except Exception:
        pass
    return 0.0


def parse_log_file(file_path):
    item = LogItem(file_path)
    parent_dirs = os.path.normpath(file_path).split(os.sep)
    parent_str = " ".join(parent_dirs).lower()
    
    lines = []
    content_head = ""
    content_tail = ""
    full_text = ""
    
    if item.file_size > 0:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                full_text = "".join(lines)
                content_head = "".join(lines[:45])
                content_tail = "".join(lines[-35:])
        except Exception:
            pass

    # 1. Parse Date and Time
    if lines:
        m_dt = re.search(r'^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', lines[0])
        if m_dt:
            item.test_date = m_dt.group(1)
            item.test_time = m_dt.group(2)
    if item.test_date == "Unknown":
        m_fn = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', item.file_name)
        if m_fn: item.test_date = m_fn.group(1).replace('_', '-')
    
    # 2. Parse Raw Headers
    m = re.search(r'Project:\s*(.+)', content_head)
    if m: item.project = m.group(1).strip()
    
    m = re.search(r'Factory ID:\s*(.+)', content_head)
    if m: item.factory_id = m.group(1).strip()
    
    m = re.search(r'Test Type:\s*(.+)', content_head)
    if m: item.test_type = m.group(1).strip()
    
    m = re.search(r'Test Name:\s*(.+)', content_head)
    if m: item.test_name = m.group(1).strip()
    
    m = re.search(r'Test Revision:\s*(.+)', content_head)
    if m: item.test_revision = m.group(1).strip()
    
    m = re.search(r'Config:\s*"([^"]+)"', content_head)
    if m: item.config_path = m.group(1).strip()

    m = re.search(r'Logs:\s*"([^"]+)"', content_head)
    if m: item.log_header_path = m.group(1).strip()

    # 3. Barcode
    m_bc = re.search(r'Scan Barcode:\s*([^\r\n]+)', full_text)
    if m_bc: item.barcode = m_bc.group(1).strip()
    else:
        m_fnbc = re.search(r'_([0-9A-Z]{10,})\.ptlog', item.file_name, re.I)
        if m_fnbc: item.barcode = m_fnbc.group(1).strip()

    # 4. Parse Pass / Fail Result
    pf_m = re.search(r'Test\s+(?:Run\s+)?(Passed|Failed)', content_tail, re.I)
    if pf_m:
        item.result = "PASS" if "pass" in pf_m.group(1).lower() else "FAIL"
    else:
        fn = item.file_name.lower()
        if "_pass" in fn or "_ok" in fn:
            item.result = "PASS"
        elif "_fail" in fn or "_ng" in fn:
            item.result = "FAIL"
        else:
            item.result = "PASS" if "passed" in parent_str else "FAIL"

    # 5. Parse Total Test Time
    tt_m = re.search(r'Total test time:\s*([0-9:.]+)', content_tail)
    if tt_m:
        item.total_time_str = tt_m.group(1).strip()
        item.total_time_sec = parse_time_to_seconds(item.total_time_str)

    # 6. Parse Numerical Measurements
    # 6.1 VDDA
    m_vdda = re.findall(r'VDDA\s*([0-9]+)\s*mV', full_text)
    if m_vdda:
        item.vdda_mv = float(m_vdda[-1])

    # 6.2 Baseline
    m_bavg = re.findall(r'Sensors global average:\s*([0-9,.]+)', full_text)
    if m_bavg:
        item.baseline_avg = float(m_bavg[-1].replace(',', ''))
        
    m_bdev = re.findall(r'Sensors deviation [^:]*:\s*([+-]?[0-9,.]+)%', full_text)
    if m_bdev:
        item.baseline_dev = float(m_bdev[-1].replace(',', ''))

    # 6.3 Untouched Deltas Grid
    delta_rows = re.findall(r'Row\d+\s+([-\d\s]+)', full_text)
    if delta_rows:
        deltas = []
        for r in delta_rows[-20:]:
            deltas.extend([int(n) for n in r.split() if n.lstrip('-').isdigit()])
        if deltas:
            item.delta_max = max(deltas)
            item.delta_min = min(deltas)

    # 6.4 Step Details (Final status per step, attempts, durations)
    step_dict = {}
    for line in lines:
        sm = re.search(r'>\s*(\d+\.\s*[^>]+)>\s*(Run started|Passed|Failed|Warning)[^\(]*(?:\(Test step time:\s*([0-9:.]+)\))?', line)
        if sm:
            s_name = re.sub(r'^\d+\.\s*', '', sm.group(1).strip())
            ev = sm.group(2).strip()
            tt_str = sm.group(3).strip() if sm.group(3) else "00:00:00"
            tt_sec = parse_time_to_seconds(tt_str)
            
            if s_name not in step_dict:
                step_dict[s_name] = {'status': 'UNKNOWN', 'attempts': 0, 'time_sec': 0.0, 'time_str': '00:00:00'}
                
            if ev == 'Run started':
                step_dict[s_name]['attempts'] += 1
            elif ev in ['Passed', 'Failed', 'Warning']:
                st = 'PASS' if 'Pass' in ev else ('WARN' if 'Warn' in ev else 'FAIL')
                step_dict[s_name]['status'] = st
                step_dict[s_name]['time_sec'] = tt_sec
                step_dict[s_name]['time_str'] = tt_str
                
        # Substep Failures & Warnings
        if '> Failed (Warning)' in line:
            w_m = re.search(r'>\s*(\d+\.\s*[^>]+)>\s*Failed\s*\(Warning\)', line)
            if w_m and w_m.group(1).strip() not in item.warning_substeps:
                item.warning_substeps.append(w_m.group(1).strip())
        elif '> Failed' in line:
            f_m = re.search(r'>\s*(\d+\.\s*[^>]+)>\s*Failed', line)
            if f_m:
                sub = f_m.group(1).strip()
                if sub not in item.failed_substeps:
                    item.failed_substeps.append(sub)

    item.step_details = step_dict
    
    # 7. Retries & Stability
    retries = sum(max(0, s_info['attempts'] - 1) for s_info in step_dict.values())
    retries += len(re.findall(r'Resetting device \(Attempt', full_text))
    item.retry_count = retries
    
    if item.result == "PASS":
        if retries > 0 or item.warning_substeps:
            item.test_stability = "Retry Recovered"
            item.is_retry_recovered = True
        else:
            item.test_stability = "Clean Pass"
    else:
        item.test_stability = "Hard Fail"

    # 8. Defect Category & Mechanism
    if item.result == "FAIL":
        for part in parent_dirs:
            if any(k in part.lower() for k in ["pin leakage", "sensor pin open", "bottom", "single point", "baseline", "untouched", "usb connect"]):
                item.defect_category = re.sub(r'^\d+\s*', '', part).strip()
                break
        if item.defect_category == "None" and item.failed_substeps:
            item.defect_category = item.failed_substeps[0]

        # Defect Mechanism Categorization
        cat_lower = (item.defect_category + " " + " ".join(item.failed_substeps)).lower()
        if "pin leakage" in cat_lower:
            item.defect_mechanism = "Pin Leakage (누설전류/쇼트)"
        elif "baseline" in cat_lower or "sensor pin open" in cat_lower:
            item.defect_mechanism = "Baseline (전극 저항/오픈)"
        elif "untouched" in cat_lower or (item.delta_min is not None and item.delta_min <= -30000):
            item.defect_mechanism = "Untouched Deltas Saturation (-32768)"
        elif "firmware" in cat_lower or "timeout" in cat_lower or "device id" in cat_lower:
            item.defect_mechanism = "Firmware / Communication Timeout"
        elif "barcode" in cat_lower:
            item.defect_mechanism = "Barcode Scan Failure"
        else:
            item.defect_mechanism = "General Defect"
    else:
        item.defect_mechanism = "Normal (양품)"

    # 9. 4-Level Normalization
    p_lower = item.project.lower()
    f_lower = item.factory_id.lower()
    
    # Level 1: Vendor
    if "toppan" in p_lower or "toppan" in parent_str:
        item.vendor = "Toppan"
    elif "dn_solutions" in p_lower or "dn솔루션" in parent_str or "sjit" in f_lower:
        item.vendor = "DN_Solutions"
    elif "yamaha" in p_lower or "casil" in f_lower or "ctm19201080t08" in parent_str:
        item.vendor = "YAMAHA_DM5"
    elif "cog-pvk0058-01" in p_lower or "boevx" in f_lower or "lcda-pvk0058" in parent_str or "lgvs" in parent_str:
        item.vendor = "BOE"
    elif item.project:
        item.vendor = re.sub(r'[\\/*?:"<>|]', '_', item.project)
    elif item.factory_id:
        item.vendor = re.sub(r'[\\/*?:"<>|]', '_', item.factory_id)
    else:
        item.vendor = "Unknown_Vendor"

    # Level 2: Model & Screen Size Category
    tn = item.test_name
    if item.vendor == "Toppan":
        item.model = "12.1_Inch"
        item.screen_size_category = "Medium (12.1\")"
    elif item.vendor == "DN_Solutions":
        if "15" in tn or "15inch" in parent_str:
            item.model = "15_Inch"
            item.screen_size_category = "Large (15\")"
        elif "24" in tn or "24inch" in parent_str:
            item.model = "24_Inch"
            item.screen_size_category = "Extra Large (24\")"
        else:
            item.model = "HMI_Sensor"
            item.screen_size_category = "Large (>=15\")"
    elif item.vendor == "YAMAHA_DM5":
        item.model = "13.3_Inch_CTM19201080T08"
        item.screen_size_category = "Medium (13.3\")"
    elif item.vendor == "BOE":
        item.model = "8_Inch_LCDA-PVK0058-05"
        item.screen_size_category = "Small (8\")"
    else:
        item.model = re.sub(r'[\\/*?:"<>| ]', '_', tn) if tn else "General_Model"
        item.screen_size_category = "Standard"

    # Level 3: Step
    tt = item.test_type
    if item.vendor == "YAMAHA_DM5":
        if "step03" in tn.lower() or "step3" in parent_str or "热压" in parent_str:
            item.step = "Step03_Sensor_FPC_Assy"
        elif "step04" in tn.lower() or "step4" in parent_str or "第一道" in parent_str:
            item.step = "Step04_Touch_Panel_Assy"
        elif "step05" in tn.lower() or "step5" in parent_str or "第二道" in parent_str or "pekotti" in tn.lower():
            item.step = "Step05_Touch_Panel_Assy_Pekotti"
        elif tt:
            item.step = re.sub(r'[\\/*?:"<>| ]', '_', tt)
        else:
            item.step = "Assy_Step"
    elif item.vendor == "DN_Solutions":
        item.step = "Sensor_FPC_Assy"
    elif item.vendor == "Toppan":
        item.step = "Module_Assy"
    elif item.vendor == "BOE":
        item.step = "Touchpanel_Assy"
    else:
        item.step = re.sub(r'[\\/*?:"<>| ]', '_', tt) if tt else "General_Step"

    return item


def classify_and_copy_logs(data_dir, output_dir, progress_callback=None):
    data_dir = os.path.abspath(data_dir)
    output_dir = os.path.abspath(output_dir)
    
    log_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.lower().endswith(".ptlog") or file.lower().endswith(".log"):
                log_files.append(os.path.join(root, file))
                
    total_files = len(log_files)
    classified_items = []
    
    os.makedirs(output_dir, exist_ok=True)
    dest_name_counts = {}

    for idx, fpath in enumerate(log_files):
        item = parse_log_file(fpath)
        
        target_dir = os.path.join(
            output_dir,
            item.vendor,
            item.model,
            item.step,
            item.result
        )
        os.makedirs(target_dir, exist_ok=True)
        
        base_name = item.file_name
        dest_candidate = os.path.join(target_dir, base_name)
        if os.path.exists(dest_candidate):
            name_part, ext_part = os.path.splitext(base_name)
            count = dest_name_counts.get(dest_candidate, 1)
            dest_name_counts[dest_candidate] = count + 1
            dest_candidate = os.path.join(target_dir, f"{name_part}_dup{count}{ext_part}")
            
        shutil.copy2(item.src_path, dest_candidate)
        item.dest_path = dest_candidate
        classified_items.append(item)
        
        if progress_callback:
            progress_callback(idx + 1, total_files, item)

    return classified_items
