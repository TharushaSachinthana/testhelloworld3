import os
import requests
import sys
import time

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN is not set.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def find_related_repo():
    query = "topic:software-engineering topic:ai topic:it sort:stars"
    url = f"https://api.github.com/search/repositories?q={query}&per_page=1"
    print(f"Searching for related repositories: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
        print("GitHub API rate limit exceeded. Try again later.")
        sys.exit(1)
    response.raise_for_status()
    items = response.json().get('items', [])
    if not items:
        print("No related repositories found.")
        sys.exit(1)
    repo_full_name = items[0]['full_name']
    print(f"Selected repository: {repo_full_name}")
    return repo_full_name

def fetch_discussions(repo):
    url = f"https://api.github.com/repos/{repo}/discussions"
    print(f"Fetching discussions from {repo}...")
    response = requests.get(url, headers=headers)
    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
        print("GitHub API rate limit exceeded. Try again later.")
        sys.exit(1)
    response.raise_for_status()
    discussions = response.json()
    if not discussions:
        print("No discussions found in this repository.")
    return discussions

def generate_answer(question):
    # TODO: Replace with your AI logic, e.g., call OpenAI API
    return f"This is an automated answer to: {question[:50]}..."

def post_answer(repo, discussion_number, answer):
    url = f"https://api.github.com/repos/{repo}/discussions/{discussion_number}/comments"
    data = {"body": answer}
    print(f"Posting answer to discussion #{discussion_number}...")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
        print("GitHub API rate limit exceeded. Try again later.")
        sys.exit(1)
    if response.status_code == 422:
        print(f"Already answered or cannot post to discussion #{discussion_number}.")
        return None
    response.raise_for_status()
    return response.json()

def main():
    repo = find_related_repo()
    discussions = fetch_discussions(repo)
    if not discussions:
        print("No discussions to answer. Exiting.")
        return
    for discussion in discussions:
        question = discussion.get('title', '') + '\n' + discussion.get('body', '')
        answer = generate_answer(question)
        result = post_answer(repo, discussion['number'], answer)
        if result:
            print(f"Answered discussion #{discussion['number']} in {repo}")
        time.sleep(2)  # Be polite to the API

if __name__ == "__main__":
    main()
