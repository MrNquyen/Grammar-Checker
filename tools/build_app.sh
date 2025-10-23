pyinstaller --onefile --distpath . `
  --add-data="templates;templates" `
  --add-data="static;static" `
  --add-data="config;config" `
  --add-data="projects;projects" `
  --add-data="tools;tools" `
  --add-data="utils;utils" `
  --add-data=".env;." `
  app.py
