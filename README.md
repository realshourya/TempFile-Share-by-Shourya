# TempShare — Python Flask

Temporary file-sharing website.

## Features
- Upload a file
- Generate a unique download link
- Link expires after 24 hours
- Expired files are deleted
- Drag and drop
- 100 MB upload limit
- SQLite database

## Run

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
python app.py
```

Open:
http://127.0.0.1:5000

## Note
This version uses possession of a random temporary URL as access control. Anyone who has the valid link can download the file. For the original assignment's authenticated-user requirement, authentication would need to be added.
