import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from markdownify import markdownify

import json

SHARIF_AC_MOTHER_LINKS = [
    "https://ac.sharif.edu/rules/"
]

DOWNLOAD_DIR = "data"


def download_and_convert_rule(url, title, edit_date):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        main_content = soup.find('main', id='writr__main')

        description = main_content.find(class_='description')
        if description:
            description.decompose()

        content_to_save = markdownify(str(main_content), heading_style="ATX")

        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        if not safe_title:
            safe_title = "unknown_rule"

        rule_folder = os.path.join(DOWNLOAD_DIR, safe_title)
        if not os.path.exists(rule_folder):
            os.makedirs(rule_folder)

        filename = f"{safe_title}.md"
        filepath = os.path.join(rule_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_to_save)
        print(f"Saved content: {filepath}")

        metadata = {
            "title": title,
            "url": url,
            "last_edit_date": edit_date,
            "file_name": filename
        }
        metadata_path = os.path.join(rule_folder, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print(f"Saved metadata: {metadata_path}")

    except Exception as e:
        print(f"Failed to process {url}: {e}")


if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

for base_url in SHARIF_AC_MOTHER_LINKS:
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', class_='dataplugin_table')

        rows = table.find_all('tr')

        for row in rows[1:]:
            cells = row.find_all('td')
            if not cells:
                continue

            first_cell = cells[0]
            link_tag = first_cell.find('a')

            if link_tag and 'href' in link_tag.attrs:
                href = link_tag['href']
                title = link_tag.get_text(strip=True)
                full_url = urljoin(base_url, href)

                date_cell = cells[1] if len(cells) > 1 else None
                edit_date = date_cell.get_text(
                    strip=True) if date_cell else "Unknown"

                print(f"Found Rule: {title} ({edit_date}) -> {full_url}")

                download_and_convert_rule(full_url, title, edit_date)

    except Exception as e:
        print(f"Error crawling {base_url}: {e}")
