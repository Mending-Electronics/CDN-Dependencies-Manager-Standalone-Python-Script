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
            if file.endswith('.html') or file.endswith('.php') or file.endswith('.py') or file.endswith('.vue') or file.endswith('.jsx') or file.endswith('.js'):
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
                                    file_name = parts[-1].replace("');", "")
                                    source = 'cdnjs.cloudflare.com'
                                else:
                                    raise IndexError("Invalid URL structure for cdnjs.cloudflare.com")
                            elif 'unpkg.com' in match:
                                if len(parts) >= 5:
                                    package_name = parts[3]
                                    version = parts[4]
                                    file_name = parts[-1].replace("');", "")
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
                                    file_name = parts[-1].replace("');", "")
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
    global temp_dep_item
    temp_dep_item = []

    print("\n*** API Request ***\n")
    for dep_file, deps in dependencies.items():
        for dep in deps:
            # Check if the API request was already made for this dependency
            matched_item = next((item for item in temp_dep_item if item['source'] == dep['source'] and item['name'] == dep['name'] and item['file'] == dep['file']), None)
            if matched_item:
                dep['new'] = matched_item['new']
                print(f"API request was already made for : {dep['source']} - {dep['name']} - {dep['file']}")
            else:
                print(f"\nRequest {dep['source']} API to get the latest version of {dep['name']} :")
                try:
                    if dep['source'] == 'cdnjs.cloudflare.com':
                        url = f"https://api.cdnjs.com/libraries/{dep['name']}"
                        print(f"{url}")
                    elif dep['source'] == 'unpkg.com':
                        url = f"https://registry.npmjs.org/{dep['name']}"
                        print(f"{dep['name']}")
                    elif dep['source'] == 'cdn.jsdelivr.net':
                        url = f"https://data.jsdelivr.com/v1/package/npm/{dep['name']}"
                        print(f"{url}")
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
                        print(f"latest cdn version : {dep['new']}\n")
                        
                        # Append the result to the global temp dictionary variable
                        temp_dep_item.append({
                            'source': dep['source'],
                            'name': dep['name'],
                            'file': dep['file'],
                            'new': dep['new'],
                        })
                    else:
                        print(f"\nFailed to fetch latest version for {dep['name']} from {dep['source']}")
                except Exception as e:
                    print(f"\nError fetching latest version for {dep['name']}: {e}")

dependencies = list_cdn_dependencies(os.getcwd())
fetch_latest_versions(dependencies)

packages_json = {
    'dependencies': dependencies
}

with open('packages.json', 'w') as f:
    json.dump(packages_json, f, indent=2)

print('\npackages.json created with CDN dependencies')

# Create a Tkinter window with a table to display the data
def display_dependencies():
    with open('packages.json', 'r') as f:
        data = json.load(f)

    root = tk.Tk()
    root.title("CDN Dependencies Manager")
    root.configure(bg='#0f2537')  # Set window background color

    try:
        # Set default icon from imageres.dll
        icon_path = os.path.join(os.environ['SystemRoot'], 'System32', 'imageres.dll')
        root.iconbitmap(icon_path)
    except:
        print("\nicon not vailable")


    # Labels
    label = tk.Label(root, text="CDN Dependencies Manager", font=("Arial",20), bg='#0f2537', fg='white').pack(pady=15)

    # Labels
    text_widget = tk.Text(root, bg='#0f2537', fg='white', font=("Arial", 12), width=70, height=1)
    text_widget.insert(tk.END, "Double click on ")
    text_widget.insert(tk.END, " Patch It now ! ", ("patch_style"))
    text_widget.insert(tk.END, " text to patch the latest cdn version in the project file.")

    text_widget.tag_configure("patch_style", font=("Arial", 10), background='yellow', foreground='black')
    text_widget.tag_configure("center", justify='center')

    text_widget.tag_add("center", "1.0", "end")

    text_widget.pack()

    # Add a "Patch All!" button
    style = ttk.Style()
    style.configure("TButton", background='#0f2537', foreground='black')

    patch_all_button = ttk.Button(root, text=" Patch All ! ", style="TButton")
    patch_all_button.pack(pady=10)  # Add 10px vertical margin


    # Add dependencies table
    tree = ttk.Treeview(root, columns=('dependencies file', 'package_name', 'file', 'version',  'new', 'source', 'patch'), show='headings')

    # Define headings
    tree.heading('dependencies file', text='Project File')
    tree.heading('package_name', text='Package Name')
    tree.heading('file', text='File')
    tree.heading('version', text='Version')
    tree.heading('new', text='Latest Version')
    tree.heading('source', text='Source')
    tree.heading('patch', text='Patch')

    # Define column properties
    tree.column('dependencies file', anchor='w', width=400)
    tree.column('package_name', anchor='w', width=120)
    tree.column('file', anchor='w')
    tree.column('version', anchor='center', width=100)
    tree.column('new', anchor='center', width=100)
    tree.column('source', anchor='w', width=120)
    tree.column('patch', anchor='center', width=100)

    for dep_file, deps in data['dependencies'].items():
        for dep in deps:
            if dep['version'] != dep['new'] and dep['new'] != '' :
                tree.insert('', 'end', values=(dep_file, dep['name'], dep['file'], dep['version'], dep['new'], dep['source'], 'Patch It now !'), tags=('mismatch',))
            else:
                tree.insert('', 'end', values=(dep_file, dep['name'], dep['file'], dep['version'], dep['new'], dep['source'], '🟢'), tags=('match',))

    tree.tag_configure('mismatch', background='yellow')
    tree.tag_configure('match', background='')

    def patch_dependency(event=None, item=None, show_message=True):
        if item is None:
            selected_item = tree.selection()[0]
        else:
            selected_item = item
        values = tree.item(selected_item, 'values')
        dep_file, package_name, file, version, new_version, source, _ = values

        if new_version == '':
            if show_message:
                # Show a message box to inform the user that the CDN latest version was not fetched
                messagebox.showerror("Patch Error", f"The latest version of the CDN for {package_name} was not fetched.")
        else:
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
            tree.item(selected_item, values=(dep_file, package_name, file, new_version, new_version, source, '🟢'), tags=('match',))
            tree.tag_configure('match', background='')

            if show_message:
                # Show a message box to inform the user that the CDN was correctly patched
                messagebox.showinfo("Patch Successful", f"The CDN for {package_name} in {dep_file} was successfully patched to version {new_version}.")

    def patch_all():
        for item in tree.get_children():
            if 'mismatch' in tree.item(item, 'tags'):
                patch_dependency(item=item, show_message=False)
        # Show a message box to inform the user that all CDNs were correctly patched
        messagebox.showinfo("Patch Successful", "All Project files were successfully patched to the latest CDN versions.")

    patch_all_button.config(command=patch_all)


    tree.bind('<Double-1>', patch_dependency)

    tree.pack(expand=True, fill='both')
    root.mainloop()

display_dependencies()
