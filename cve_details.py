import requests
from bs4 import BeautifulSoup
import subprocess
import re
import os
import json

# Define URLs and other constants
cve_list_url = "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword="
poc_search_url = "https://www.google.com/search?q="
hackerone_search_url = "https://hackerone.com/reports?filter=type%3Apublic&filter=state%3Atriaged&page="
github_search_url = "https://api.github.com/search/repositories?q="
github_token = os.environ.get("GITHUB_TOKEN")  # Set the GITHUB_TOKEN environment variable to use the GitHub API

# Define functions for PoC searching
def get_poc_urls(cve):
    url = poc_search_url + cve + "+poc"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    poc_urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href.startswith("http") and not "google" in href:
            poc_urls.append(href)
    return poc_urls

def check_references_for_poc(cve):
    references_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve
    response = requests.get(references_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    references = soup.find('td', {'valign': 'top', 'colspan': '6'}).find_all('a')
    
    poc_references = []
    for reference in references:
        if re.search(r'(?i)[^a-z0-9]+(poc|proof of concept|proof[-_]of[-_]concept)[^a-z0-9]+', reference.text):
            poc_references.append(reference)
    
    return poc_references

# Define functions for HackerOne searching
def get_hackerone_reports(cve):
    reports_url = hackerone_search_url + "&q=" + cve
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(reports_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    report_links = [link.get("href") for link in soup.find_all("a", {"class": "report-link"})]
    return report_links

def get_hackerone_pocs(cve):
    pocs = []
    print(f"Searching for HackerOne reports for {cve}...")
    page_num = 1
    while True:
        reports = get_hackerone_reports(cve + "&page=" + str(page_num))
        if not reports:
            break
        for report in reports:
            report_response = requests.get(report, headers=headers)
            report_soup = BeautifulSoup(report_response.content, "html.parser")
            if report_soup.find("h1", {"class": "title"}).text == "Report not available":
                continue
            poc_links = report_soup.find_all("a", href=re.compile(".(gif|jpg|png|pdf|mp4)$"))
            for poc_link in poc_links:
                pocs.append(poc_link.get("href"))
        page_num += 1
    return pocs

# Define functions for GitHub searching
def search_github(cve):
    url = github_search_url + cve + "+language:python+repo:find-gh-poc"
    headers = {"Accept": "application/vnd.github.mercy-preview+json",
               "Authorization": "token " + github_token}
    response = requests.get(url, headers=headers)
    repos = [item["html_url"] for item in response.json()["items"]]
    return repos

def download_github_files(cve, repos):
    cve_dir = os.path.join("output", cve)
    if not os.path.exists(cve_dir):
        os.makedirs(cve_dir)
    for repo in repos:
        print(f"Downloading files from {repo}...")
        output_dir = os.path.join(c
