# Python 3.11
# JALLET Alexandre

import os
import re
import json
import requests
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

def list_cdn_dependencies(dir):
    dependencies = {}
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.js') or file.endswith('.html') or file.endswith('.php') or file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    cdn_matches = re.findall(r'https://(?:cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|unpkg\.com)/[^"\s]+', content)
                    for match in cdn_matches:
                        try:
                            # Extract package name, version, and file name
                            parts = match.split('/')
                            if 'cdnjs.cloudflare.com' in match:
                                if len(parts) >= 7:
                                    package_name = parts[5]
                                    version = parts[6]
                                    file_name = parts[-1]
                                    source = 'cdnjs.cloudflare.com'
                                else:
                                    raise IndexError("Invalid URL structure for cdnjs.cloudflare.com")
                            elif 'unpkg.com' in match:
                                if len(parts) >= 5:
                                    package_name = parts[3]
                                    version = parts[4]
                                    file_name = parts[-1]
                                    source = 'unpkg.com'
                                else:
                                    raise IndexError("Invalid URL structure for unpkg.com")
                            elif 'cdn.jsdelivr.net' in match:
                                if len(parts) >= 6:
                                    package_name_version = parts[4]
                                    if '@' in package_name_version:
                                        package_name, version = package_name_version.split('@')
                                    else:
                                        raise ValueError("Invalid package name and version format for cdn.jsdelivr.net")
                                    file_name = parts[-1]
                                    source = 'cdn.jsdelivr.net'
                                else:
                                    raise IndexError("Invalid URL structure for cdn.jsdelivr.net")
                            else:
                                raise ValueError("Unknown CDN format")
                            
                            relative_path = os.path.relpath(os.path.join(root, file), dir)
                            
                            if relative_path not in dependencies:
                                dependencies[relative_path] = []
                            
                            dependencies[relative_path].append({
                                'name': package_name,
                                'version': version,
                                'new': '',
                                'file': file_name,
                                'cdn': match,
                                'source': source
                            })
                        except (IndexError, ValueError) as e:
                            print(f"Error processing URL: {match} - {e}")
    return dependencies

def fetch_latest_versions(dependencies):

    print("\n*** API Request ***\n")
    for dep_file, deps in dependencies.items():
        for dep in deps:
            print(f"Request {dep['source']} API to get the latest version of {dep['name']} :")
            try:
                if dep['source'] == 'cdnjs.cloudflare.com':
                    url = f"https://api.cdnjs.com/libraries/{dep['name']}"
                    print(f"{url}\n")
                elif dep['source'] == 'unpkg.com':
                    url = f"https://registry.npmjs.org/{dep['name']}"
                    print(f"{dep['name']}\n")
                elif dep['source'] == 'cdn.jsdelivr.net':
                    url = f"https://data.jsdelivr.com/v1/package/npm/{dep['name']}"
                    print(f"{url}\n")
                else:
                    continue
                
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if dep['source'] == 'cdnjs.cloudflare.com':
                        dep['new'] = data['version']
                    elif dep['source'] == 'unpkg.com':
                        dep['new'] = data['dist-tags']['latest']
                    elif dep['source'] == 'cdn.jsdelivr.net':
                        dep['new'] = data['tags']['latest']
                else:
                    print(f"Failed to fetch latest version for {dep['name']} from {dep['source']}")
            except Exception as e:
                print(f"Error fetching latest version for {dep['name']}: {e}")

dependencies = list_cdn_dependencies(os.getcwd())
fetch_latest_versions(dependencies)

packages_json = {
    'dependencies': dependencies
}

with open('packages.json', 'w') as f:
    json.dump(packages_json, f, indent=2)

print('packages.json created with CDN dependencies')

# Create a Tkinter window with a table to display the data
def display_dependencies():
    with open('packages.json', 'r') as f:
        data = json.load(f)

    root = tk.Tk()
    root.title("CDN Dependencies")

    label = tk.Label(root, text="CDN Dependencies", font=("Arial",30)).pack()

    label = tk.Label(root, text="Double click on 'Patch It now !' text to patch the cdn.", font=("Arial",8)).pack()

    tree = ttk.Treeview(root, columns=('dependencies file', 'package_name', 'file', 'version',  'new', 'source', 'patch'), show='headings')
    tree.heading('dependencies file', text='Project File')
    tree.heading('package_name', text='Package Name')
    tree.heading('file', text='File')
    tree.heading('version', text='Version')
    tree.heading('new', text='New Version')
    tree.heading('source', text='Source')
    tree.heading('patch', text='Patch')

    for dep_file, deps in data['dependencies'].items():
        for dep in deps:
            if dep['version'] != dep['new']:
                tree.insert('', 'end', values=(dep_file, dep['name'], dep['file'], dep['version'], dep['new'], dep['source'], 'Patch It now !'), tags=('mismatch',))
            else:
                tree.insert('', 'end', values=(dep_file, dep['name'], dep['file'], dep['version'], dep['new'], dep['source'], ''), tags=('match',))

    tree.tag_configure('mismatch', background='yellow')
    tree.tag_configure('match', background='')

    def patch_dependency(event):
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, 'values')
        dep_file, package_name, file, version, new_version, source, _ = values

        # Read the dep_file from the current directory
        with open(dep_file, 'r') as f:
            content = f.read()

        # Search for the dep['cdn'] line in the file and replace the dep['version'] with the dep['new']
        for dep in data['dependencies'][dep_file]:
            if dep['name'] == package_name and dep['version'] == version:
                old_cdn = dep['cdn']
                new_cdn = old_cdn.replace(version, new_version)
                content = content.replace(old_cdn, new_cdn)
                dep['version'] = new_version

        # Save the updated content back to the file
        with open(dep_file, 'w') as f:
            f.write(content)

        # Save the updated dependencies to the packages.json file
        with open('packages.json', 'w') as f:
            json.dump(data, f, indent=2)

        # Update the table
        tree.item(selected_item, values=(dep_file, package_name, file, new_version, new_version, source, ''), tags=('match',))
        tree.tag_configure('match', background='')

        # Show a message box to inform the user that the CDN was correctly patched
        messagebox.showinfo("Patch Successful", f"The CDN for {package_name} in {dep_file} was successfully patched to version {new_version}.")

    tree.bind('<Double-1>', patch_dependency)


    tree.bind('<Double-1>', patch_dependency)

    tree.pack(expand=True, fill='both')
    root.mainloop()

display_dependencies()
