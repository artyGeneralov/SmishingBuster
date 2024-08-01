import requests
import os
def main():
    url="https://t.ly/clykf"
    result = check_url_with_virustotal(url)
    score = score_by_result(result['scans'])
    print(score)

def analyze_link_virustotal(url):
    print(url)
    api_key = os.getenv("VIRUS_TOTAL_API_ART")
    if not api_key:
        raise ValueError("VIRUS_TOTAL_API_ART environment variable is not set")
    try:
        result = check_url_with_virustotal(url, api_key)
        if result is None:
            return 0
        score = score_by_result(result['scans'])
        return score
    except Exception as e:
        print("Error:", e)
        return 0

def analyze_link_google_safe_browsing(url):
    pass

def score_by_result(result):
    total_vendors = 0
    unsafe_vendors = 0
    for vendor, res in result.items():
        if res['result'] != 'unrated site':
            total_vendors += 1
            if res['detected']:
                unsafe_vendors += 1
    return round((unsafe_vendors / total_vendors) * 100 , 2)


def check_url_with_virustotal(url, api_key):
    scan_url = "https://www.virustotal.com/vtapi/v2/url/scan"
    scan_params = {"apikey": api_key, "url": url}
    scan_response = requests.post(scan_url, data=scan_params)
    
    scan_result = scan_response.json()
    if isinstance(scan_result, list) and all(item.get('response_code') == -1 for item in scan_result):
        print("Invalid URL or other error:", scan_result)
        return None
    
    resource = scan_result.get("scan_id")
    
    report_url = "https://www.virustotal.com/vtapi/v2/url/report"
    report_params = {"apikey": api_key, "resource": resource}
    report_response = requests.get(report_url, params=report_params)
    return report_response.json()

if __name__ == "__main__":
    main()