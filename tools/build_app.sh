pyinstaller --onefile --noconsole `
  --add-data="templates;templates" `
  --add-data="static;static" `
  --add-data="config;config" `
  --add-data="projects;projects" `
  --add-data="save;save" `
  --add-data="tools;tools" `
  --add-data="utils;utils" `
  --add-data=".env;." `
  app.py
