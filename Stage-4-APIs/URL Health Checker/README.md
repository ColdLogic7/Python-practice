# 🌐 URL Health Checker

A Python CLI tool that checks website availability, response time, HTTP status codes, and redirects. Supports checking a single URL or multiple URLs concurrently.

## ✨ Features
- Check a single URL or a list from a text file.
- Categorize results as Online, Redirected, or Failed.
- Measure response time and detect redirects.
- Check multiple URLs using concurrent threads.
- Export results and summary to `report.csv`.

## 🛠 Skills Practiced
- `requests` and HTTP responses
- `ThreadPoolExecutor` and concurrency
- `argparse` for CLI arguments
- CSV file handling
- Exception handling and URL parsing

## 🚀 How To Run

Install the dependency:

```bash
pip install requests
```

Check one URL:

```bash
python url_health_checker.py --url https://example.com
```

Check URLs from a file:

```bash
python url_health_checker.py --file urls.txt
```

## 📂 Project Structure

```text
url-health-checker/
├── url_health_checker.py
├── urls.txt
├── report.csv
└── README.md
```

## 📚 What I Learned — Project 14/26
- Running multiple HTTP requests concurrently.
- Using `ThreadPoolExecutor` to improve efficiency.
- Building command-line tools with `argparse`.
- Generating structured CSV reports.

## 💡 Biggest Takeaway

Concurrency makes repetitive network tasks faster, while structured results make them easier to analyze.

## 📈 Roadmap Progress
**14 / 26 Projects Completed** — 54%

## 👨‍💻 Author

**ColdLogic7**

Learning Python through project-based practice and documenting lessons along the way.