import re
import argparse
from termcolor import colored
import requests
import chardet


def parse_script_arguments():
    parser = argparse.ArgumentParser(
        description='Parse script input parameters into a dictionary')

    parser.add_argument('--urls', type=str, help='URLs')
    parser.add_argument('--wordlist', type=str, help='Wordlist')

    args = parser.parse_args()

    parameters = {
        'urls': args.urls,
        'wordlist': args.wordlist,
    }

    global urlsFilename, wordlistFilename, saveFilename
    urlsFilename = parameters['urls']
    wordlistFilename = parameters['wordlist']

    return parameters


parse_script_arguments()

# Read the list of URLs to test from a file
with open(urlsFilename, "rb") as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    encoding = result["encoding"]

with open(urlsFilename, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f.readlines()]


# Set the list of payloads to test
with open(wordlistFilename, "r") as f:
    payloads = [line.strip() for line in f.readlines()]

# Iterate through each URL and payload
vulnerable_urls = []
total_requests = len(urls) * len(payloads)
progress = 0

for url in urls:
    for payload in payloads:
        try:
            # Split the URL into its individual parameters
            url_params = url.split("&")

            # Iterate through each parameter and replace the value with the payload
            for i, param in enumerate(url_params):
                if "=" in param:
                    param_name, param_value = param.split("=")
                    url_params[i] = f"{param_name}={payload}"

            # Reconstruct the URL with the modified parameters and send the request
            request_url = "&".join(url_params)
            response = requests.get(request_url)

            # Check if the response time is greater than 15 seconds
            if response.elapsed.total_seconds() >= 15:
                # Highlight vulnerable URLs in red bold
                url_payload = re.sub(r":hacked$", "", request_url)
                print(colored(url_payload, 'red', attrs=[
                      'bold']) + colored(" hacked", 'white'))
                vulnerable_urls.append(request_url)
            else:
                # Print safe URLs in green text
                print(colored(f"{request_url} safe", 'green'))

            # Print elapsed time
            elapsed_time = round(response.elapsed.total_seconds(), 2)
            print(f"Elapsed time: {elapsed_time}s")

            # Update progress and calculate estimated remaining time
            progress += 1
            elapsed_seconds = response.elapsed.total_seconds()
            remaining_seconds = (total_requests - progress) * \
                (elapsed_seconds / progress)
            remaining_hours = int(remaining_seconds // 3600)
            remaining_minutes = int((remaining_seconds % 3600) // 60)
            percent_complete = round(progress / total_requests * 100, 2)

            # Print progress update
            print(f"{colored('Progress:', 'blue')} {progress}/{total_requests} ({percent_complete}%) - {remaining_hours}h:{remaining_minutes:02d}m")

        except Exception as e:
            print(f"An error occurred: {e}. Saving vulnerable URLs to file...")
            break

# Save vulnerable URLs to file

print("Printing vulnerable URLs...")
print("Found {} vulnerable URLs.".format(len(vulnerable_urls)))
for url in vulnerable_urls:
    print(url)
