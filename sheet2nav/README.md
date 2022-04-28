# sheet2nav

This is a quick tool used to convert a Google Sheet into MITRE ATT&CK Navigator JSON. 

# Installation

1. Use your favorite virtualenv solution to create a virtual python environment.
2. Install dependencies:
`pip3 install -r requirements.txt`

# Instructions

1. You will need a Google Cloud account to generate auth key to use Google Sheets API.
2. Import the template/nav2sheet.csv template into Google Sheets. You will use this format to document your TTPs.
3. Add the Google Sheet API user as an editor of your newly imported sheet.
3. Run the tool:
`python3 sheet2nav.py --auth googleapi.json -s "Mac Malware of 2021" -os macOS`

- The -s argument is the name of your Google Sheet.
- the -os argument is the platforms. You can add 1, or mulitple. For mulitple, here are your options:

    "Linux"
    "macOS"
    "Windows"
    "PRE"
    "Containers"
    "Network"
    "Office 365"
    "SaaS"
    "Google Workspace"
    "IaaS"
    "Azure AD
- Multiple platforms are passed as an argument with space as a delimitter. An example execution specifying multiple platforms:
`python3 sheet2nav.py --auth googleapi.json -s "Mac Malware of 2021" -os macOS Windows Linux`

# Example

1. This tool will take a Google Sheet file that looks like this:
![googlesheet](/sheet2nav/assets/googlesheet.png?raw=true)

2. Into this:
![navigator](/sheet2nav/assets/navigator.png?raw=true)

3. The reports directory contains an example Navigator file this tool will generate. You can import this file here: https://mitre-attack.github.io/attack-navigator
