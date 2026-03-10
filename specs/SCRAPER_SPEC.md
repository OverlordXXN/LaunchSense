# SCRAPER_SPEC_v2

OBJECTIVE

Collect snapshots of live Kickstarter projects.

SCRAPER MODE

Manual execution only.

Command:

python src/scraper/run_scraper.py

DISCOVERY

Use discover page:

https://www.kickstarter.com/discover/advanced?state=live

Pagination:

?page=1
?page=2

Continue until no projects found.

PROJECT EXTRACTION

For each project page extract data from JSON embedded in:

<script id="__NEXT_DATA__">

FIELDS

project_id
name
category
goal
pledged
backers_count
state
created_at
launched_at
deadline

RATE LIMIT

Delay between requests:

2–5 seconds

MAX PROJECTS PER RUN

500

DEDUPLICATION

Skip snapshot if:

same project_id
same pledged
same backers
same day

OUTPUT

Store snapshot in database.