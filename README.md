# CDN Dependency Manager Tool

## Overview
CDN Dependency Manager is a standalone Python script designed to scan your project directory files and list all CDN dependencies used. It generates a `packages.json` file similar to a Node.js project and queries common CDN APIs to fetch the latest versions of these packages. Users can easily update the CDN versions in their project files by clicking the patch button.

## Features
- Scans CDN dependencies in *.html, *.js, *.jsx, *.vue, *.php, and *.py files.
- Generates a `packages.json` file with the listed dependencies.
- Fetches the latest versions of CDN packages from common APIs.
- Allows users to patch CDN versions with a simple click.

**CDNs Supported:**
- https://cdnjs.cloudflare.com
- https://cdn.jsdelivr.net

## Installation
1. Install Python 3.xx if you haven't already.
2. Download the script and place it in the root directory of your project.

## Usage
1. Run the script:
    ```bash
    python '# CDN Dependency Manager (Standalone).py'
    ```
2. The script will check each file in your project directory to list the CDN dependencies used in each file. It will request the CDN APIs to get the latest versions of the packages and compare them to the used CDN package versions. It will then generate a `packages.json` file.
3. Review the listed CDN dependencies and their versions in a table.
4. Click the patch button to update the CDN versions in your project files.

## Sample Captures

************

**Patch only one project file CDN version**

![Capture](https://raw.githubusercontent.com/Mending-Electronics/CDN-Dependency-Manager-Standalone-Python-Script/main/captures/capture1.png "Capture")

![Capture](https://raw.githubusercontent.com/Mending-Electronics/CDN-Dependency-Manager-Standalone-Python-Script/main/captures/capture2.png "Capture")

*************

**Patch all project files CDN versions**

![Capture](https://raw.githubusercontent.com/Mending-Electronics/CDN-Dependency-Manager-Standalone-Python-Script/main/captures/capture3.png "Capture")

![Capture](https://raw.githubusercontent.com/Mending-Electronics/CDN-Dependency-Manager-Standalone-Python-Script/main/captures/capture4.png "Capture")

![Capture](https://raw.githubusercontent.com/Mending-Electronics/CDN-Dependency-Manager-Standalone-Python-Script/main/captures/capture5.png "Capture")

## Sample 'packages.json' Output
```json
{
  "dependencies": {
    "index.html": [
      {
        "name": "bootstrap",
        "version": "5.3.3",
        "new": "5.3.3",
        "file": "bootstrap.min.css",
        "cdn": "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.3/css/bootstrap.min.css",
        "source": "cdnjs.cloudflare.com"
      },
      {
        "name": "bootstrap",
        "version": "5.2.3",
        "new": "5.3.3",
        "file": "bootstrap.min.js",
        "cdn": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js",
        "source": "cdn.jsdelivr.net"
      }
    ],
    "templates\\app.html": [
      {
        "name": "axios",
        "version": "1.7.7",
        "new": "1.7.7",
        "file": "axios.min.js",
        "cdn": "https://cdnjs.cloudflare.com/ajax/libs/axios/1.7.7/axios.min.js",
        "source": "cdnjs.cloudflare.com"
      }
    ]
  }
}
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or suggestions, please open an issue.
