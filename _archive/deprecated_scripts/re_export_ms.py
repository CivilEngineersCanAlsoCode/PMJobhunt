import json
import csv
import glob
import os
import re

DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
OUTPUT_CSV = "/Users/satvikjain/Downloads/PM/data/microsoft_pm_jobs_full.csv"

def clean_description(html):
    if not html: return ""
    # Simple clean, same as in capture scripts
    clean = html.replace('<br/>', '\n').replace('<br>', '\n')
    clean = re.sub('<[^<]+?>', '', clean) # Remove any other tags
    return clean.strip()

def re_export_microsoft():
    files = glob.glob(os.path.join(DATA_DIR, "microsoft_detail_*.json"))
    unique_jobs = {}

    print(f"[*] Processing {len(files)} Microsoft detail files...")

    for f in files:
        try:
            with open(f, 'r') as j:
                content = json.load(j)
                # Outer wrapper "data" -> inner wrapper "data"
                job_data_outer = content.get('data', {})
                job_data_inner = job_data_outer.get('data', job_data_outer) if isinstance(job_data_outer, dict) else job_data_outer
                
                job_id = job_data_inner.get('id') or job_data_inner.get('displayJobId')
                title = job_data_inner.get('name') or job_data_inner.get('title')
                
                if title and job_id and str(job_id) not in unique_jobs:
                    jd = job_data_inner.get('jobDescription') or job_data_inner.get('description', '')
                    locs = job_data_inner.get('locations')
                    if isinstance(locs, list) and locs:
                        loc = locs[0]
                    else:
                        loc = job_data_inner.get('location', 'Check JSON')
                    
                    unique_jobs[str(job_id)] = {
                        'Job Title': title,
                        'Job ID': job_id,
                        'Location': loc,
                        'Description': clean_description(jd),
                        'Apply Link': f"https://apply.careers.microsoft.com/careers/job/{job_id}"
                    }
        except Exception as e:
            print(f"  [!] Skip {os.path.basename(f)}: {e}")

    if unique_jobs:
        fieldnames = ['Job Title', 'Job ID', 'Location', 'Description', 'Apply Link']
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for jid in sorted(unique_jobs.keys()):
                writer.writerow(unique_jobs[jid])
        print(f"[+] Re-exported {len(unique_jobs)} Microsoft jobs to {OUTPUT_CSV}")

if __name__ == "__main__":
    re_export_microsoft()
