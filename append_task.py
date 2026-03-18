import os

content = """
--------------------------------------------------
PATCH TASK — SCRAPER 403 FIX (HEADERS INJECTION) [COMPLETED]
--------------------------------------------------

[X] TASK-068 update HTTP requests in crawler to include headers
[X] TASK-069 ensure response validation
[X] TASK-070 optional: introduce requests.Session()
"""

with open('d:/Proyecto_Kickstarter/specs/AGENT_TASK_TREE_v3.md', 'a', encoding='utf-8') as f:
    f.write(content)

print("Appended successfully")
