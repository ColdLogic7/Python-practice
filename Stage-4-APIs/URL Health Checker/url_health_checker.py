from concurrent.futures import ThreadPoolExecutor
import time
import requests
from urllib.parse import urlparse
import csv
import argparse
import sys
from functools import partial

def categorize_signals(status_code: int):
    # IN: status code of website
    # OUT: return online, redirect, failed signal
    if status_code is None:
        return 'Failed'
    first_digit = status_code // 100 # floor division used here e.g 200 // 100 = 2
    if first_digit == 2:
        return 'Online'
    elif first_digit == 3:
        return 'Redirected'
    else:
        return 'Failed'

def parse_url_parts(url: str):
    # IN: url
    # OUT: schema, host, path
    parts = urlparse(url)
    return parts.scheme, parts.netloc, parts.path

def check_url(url: str, timeout=5):
    # IN: url and response time
    # OUT: dictionary contains - url, status_code, status_category, response_time_ms, redirected, final_url, schema, host, path

    if not url.startswith('http') and not url.startswith('https'):
        url = 'https://' + url
    session = requests.sessions.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        start_time = time.time()
        response = session.get(url=url, timeout=timeout)
        elapsed_ms = round((time.time() - start_time) * 1000)
        schema, host, path = parse_url_parts(url)
        signal_interpret = categorize_signals(response.status_code)

        result = {
            'url': url,
            'status_code': response.status_code,
            'status_category': signal_interpret,
            'response_time_ms': elapsed_ms,
            'redirected': True if len(response.history) > 0 else False,
            'final_url': response.url,
            'schema': schema.upper(),
            'host': host,
            'path': path,
        }
        return result
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) :
        return {
            'url': url, 'status_code': None, 'status_category': 'Failed',
            'response_time_ms': None, 'redirected': None, 'final_url': None,
            'schema': None, 'host': None, 'path': None
        }
    except requests.exceptions.RequestException as err:
        print(f"\n\t [❌ An unexpected error occurred: {err}!]")


def display_single_results(result: dict):
    # IN: result variable which is a dictionary
    # OUT: display result in appealing way

    if not result:
        return "❌ Something went wrong..."
    
    if result['status_category'] == 'Online' or result['status_category'] == 'Redirected':
        print("\u2500" * 38)
        print(f"🌐 Target  :  {result['url']}")
        print("\u2500" * 38)
        print(f"Status Code   : {'✅' if result['status_category'] == 'Online' else '🔀'} {result['status_code']} ({result['status_category']})")
        print(f"Response Time : {result['response_time_ms']} ms")
        print(f"Redirected    : {'No redirection' if result['redirected'] is False else 'yes → ' + result['final_url']}")
        print(f"Final URL     : {result['final_url']}")
        print(f"Schema        : {result['schema']}")
        print(f"Host          : {result['host']}")
        print(f"Path          : {result['path']}")
        print("\u2500" * 38)

    elif result['status_category'] == 'Failed':
        print("\u2500" * 38)
        print(f"🌐 Target  :  {result['url']}")
        print("\u2500" * 38)
        print(f"Status Code   : ❌ {result['status_code']} ({result['status_category']})")
        print(f"Response Time : - ")
        print(f"Error         : Could not reach target — check URL and internet connection")
        print("\u2500" * 38)

def read_urls_from_file(filepath: str):
    # IN: filepath (contains location of provided file)
    # OUT: urls_list (A list of urls)
    if not filepath:
        print("\n⚠️ File is inaccessible!")
    try:
        with open(file=filepath, mode="r", encoding='UTF-8') as file:
            urls = file.read()
        if not urls:
            print("\n ⚠️  No URLs found in file")
            return
        urls_list = urls.splitlines()
        return urls_list
    except (FileNotFoundError, FileExistsError) as err:
        print(f"\n ⚠️ File Not Found: {err}")

def check_urls_concurrent(urls: list, timeout=5, workers=10):
    # IN: list of urls, timeout, workers value
    # OUT: list of dictionary which contain all the dictionary
    if not urls:
        return

    check_with_timeout = partial(check_url, timeout=timeout)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(check_with_timeout, urls))
    return results

def write_csv_report(results: list):
    # IN: results (list of results dictionaries)
    # OUT: write content in CSV file

    if not results:
        return

    with open('report.csv', 'w', newline='',encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['url', 'status_code','status_category', 'response_time_ms', 'final_url', 'schema', 'host', 'path'])
        writer.writeheader()

        for result in results:
            writer.writerow({
                        'url': result.get('url'),
                        'status_code': result.get('status_code'), 
                        'status_category': result.get('status_category'), 
                        'response_time_ms': result.get('response_time_ms'), 
                        'final_url': result.get('final_url'), 
                        'schema': result.get('schema'), 
                        'host': result.get('host'), 
                        'path': result.get('path')
                        })

def display_summary(results: list):
    # IN: results (list of results dictionaries)
    # OUT: print summary dashboard
    
    if not results:
        return
    
    online_urls, failed_urls, redirected_urls, avg_response_time, successful_count = 0, 0, 0, 0, 0

    for result in results:
        online_urls +=  1 if result['status_category'] == 'Online' else 0
        redirected_urls += 1 if result['status_category'] == 'Redirected' else 0
        failed_urls += 1 if result['status_category'] == 'Failed' else 0
        if result['response_time_ms'] is not None:
            avg_response_time += result['response_time_ms']
            successful_count += 1

    avg_response_time = avg_response_time / successful_count if successful_count else 0

    print(f"{'='*4} Health Check Complete {'='*4}")
    print(f"Total URLs : {len(results)}")
    print(f"✅ Online (2xx) : {online_urls}")
    print(f"🔀 Redirected : {redirected_urls}")
    print(f"❌ Failed/Timeout : {failed_urls}")
    print(f"Avg Response Time : {round(avg_response_time, 2)}")
    print(f"Report saved to : report.csv")
    
    
def main():
    parser = argparse.ArgumentParser(
        description="Website Health Checker - monitor availability, "
                    "status codes, and response time.",
        epilog="Check: Status Code, Response Time, Redirection, Schema, Host, Path."
    )
    parser.add_argument('-u','--url',type=str, 
                        help='Single url to check e.g http://example.com')
    parser.add_argument('-f', '--file', type=str,
                        help='Text file of URLs, one per line e.g urls.txt')
    parser.add_argument('--timeout', type=int, default=5,
                        help="Request timeout in seconds (default: 5)")
    parser.add_argument('--workers', type=int, default=5,
                        help='Concurrent threads for file mode (default: 10)')
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    if args.url:
        dict_result = check_url(url=args.url, timeout=args.timeout)
        display_single_results(result=dict_result)

    elif args.file:
        urls_list = read_urls_from_file(filepath=args.file)
        results_list = check_urls_concurrent(urls=urls_list, workers=args.workers)
        write_csv_report(results=results_list)
        display_summary(results=results_list)

if __name__ == '__main__':
    main()
