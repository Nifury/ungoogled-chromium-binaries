import datetime
import glob
import hashlib
import os.path
import re

import requests
from tqdm import tqdm

content = requests.get('https://github.com/ungoogled-software/ungoogled-chromium-windows/releases').text
s = '<a href="/ungoogled-software/ungoogled-chromium-windows/tree/'
idx1 = content.index(s) + len(s)
idx2 = content.index('"', idx1)
tag = content[idx1:idx2]
print(tag)
config = [
    ('32bit', 'x86'),
    ('64bit', 'x64'),
]
endings = [
    ('installer', 'exe'),
    ('windows', 'zip'),
]
hashes = (('md5', hashlib.md5), ('sha1', hashlib.sha1), ('sha256', hashlib.sha256))
for c_path, c_name in tqdm(config):
    lines = []
    lines.append('[_metadata]')
    lines.append(f'publication_time = {datetime.datetime.utcnow().isoformat()}')
    lines.append('github_author = github-actions')
    lines.append('# Add a `note` field here for additional information. Markdown is supported')

    for ending in endings:
        lines.append('')
        name = f'ungoogled-chromium_{tag}_{ending[0]}_{c_name}.{ending[1]}'
        lines.append(f'[{name}]')
        lines.append(f'url = https://github.com/ungoogled-software/ungoogled-chromium-windows/releases/download/{tag}/{name}')

        with requests.get(f'https://github.com/ungoogled-software/ungoogled-chromium-windows/releases/download/{tag}/{name}', stream=True) as r:
            hash_instances = [(h_name, h()) for h_name, h in hashes]
            for chunk in r.iter_content(65536):
                for _, h in hash_instances:
                    h.update(chunk)
        for h_name, h in hash_instances:
            h = h.hexdigest()
            lines.append(f'{h_name} = {h}')
    with open(f'config\\platforms\\windows\\{c_path}\\{tag[:-2]}.ini', 'w') as f:
        f.write('\n'.join(lines))

