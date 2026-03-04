"""
build_final_batch.py
Consolidates top 3 most relevant PM jobs from Google, Microsoft, and Amazon
into a single final_job_batch.csv.
"""
import csv
import os
import re

# Determine the directory of the current script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT = os.path.join(DATA_DIR, "final_job_batch.csv")

# Top 3 hand-picked most relevant Google PM jobs
GOOGLE_TOP3 = [
    "85393000904958662",   # Product Manager, YouTube Live Living Room
    "139227259159356102",  # Product Manager, Studio, Foundations, YouTube
    "100219517855302342",  # Product Manager, Studio, GenAI, YouTube
]

# Top 3 hand-picked Microsoft PM jobs (AI/Cloud/Enterprise)
MICROSOFT_TOP3_KEYWORDS = [
    "Product Manager-II",
    "Principal Product Manager",
    "Senior Product Manager",
]

# Top 3 Amazon PM jobs keywords
AMAZON_TOP3_KEYWORDS = [
    "Product Manager",
]

def read_csv(path):
    if not os.path.exists(path):
        print(f"  [!] File not found: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def select_top_google(google_jobs, ids):
    """Pick top 3 by job ID list."""
    selected = [j for j in google_jobs if str(j.get("Job ID", "")) in ids]
    if len(selected) < 3:
        # Fill with additional jobs if IDs don't match
        for j in google_jobs:
            if len(selected) >= 3: break
            if j not in selected:
                selected.append(j)
    return selected[:3]

def select_top_microsoft(ms_jobs):
    """Pick 3 diverse, relevant PM roles from Microsoft."""
    scored = []
    priority_keywords = ["AI", "Cloud", "Platform", "Azure", "GenAI", "Enterprise", 
                         "M365", "Security", "Copilot", "Intelligence"]
    for j in ms_jobs:
        title = j.get("Job Title", "").lower()
        score = 0
        if "principal" in title: score += 3
        if "senior" in title: score += 2
        for kw in priority_keywords:
            if kw.lower() in title: score += 1
        scored.append((score, j))
    scored.sort(key=lambda x: -x[0])
    return [j for _, j in scored[:3]]

def select_top_amazon(amz_jobs):
    """Pick 3 most relevant Amazon PM roles."""
    scored = []
    priority_keywords = ["Technical", "Senior", "Principal", "AI", "Machine Learning",
                         "Cloud", "AWS", "Platform", "GenAI", "Data"]
    for j in amz_jobs:
        title = j.get("Job Title", "").lower()
        score = 0
        if "principal" in title: score += 3
        if "senior" in title: score += 2
        if "technical" in title: score += 2
        for kw in priority_keywords:
            if kw.lower() in title: score += 1
        scored.append((score, j))
    scored.sort(key=lambda x: -x[0])
    return [j for _, j in scored[:3]]

def build_final_batch():
    print("[*] Reading source CSV files...")
    
    google_jobs = read_csv(os.path.join(DATA_DIR, "Google_manual_jobs.csv"))
    ms_jobs = read_csv(os.path.join(DATA_DIR, "microsoft_pm_jobs_full.csv"))
    amz_jobs = read_csv(os.path.join(DATA_DIR, "Amazon_manual_jobs.csv"))
    
    print(f"    Google: {len(google_jobs)} jobs")
    print(f"    Microsoft: {len(ms_jobs)} jobs")
    print(f"    Amazon: {len(amz_jobs)} jobs")

    top_google = select_top_google(google_jobs, GOOGLE_TOP3)
    top_ms = select_top_microsoft(ms_jobs)
    top_amz = select_top_amazon(amz_jobs)

    final = []
    for company, jobs in [("Google", top_google), ("Microsoft", top_ms), ("Amazon", top_amz)]:
        for j in jobs:
            row = dict(j)
            row["Company"] = company
            final.append(row)
    
    fieldnames = ["Company", "Job Title", "Job ID", "Location", "Description", "Apply Link"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(final)
    
    print(f"\n[✅] Final batch written → {OUTPUT}")
    print(f"     {len(final)} total jobs ({len(top_google)} Google, {len(top_ms)} Microsoft, {len(top_amz)} Amazon)\n")
    
    for row in final:
        print(f"  [{row['Company']}] {row['Job Title']}")

if __name__ == "__main__":
    build_final_batch()
