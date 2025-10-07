pyinstaller --onefile --noconsole `
  --add-data="templates;templates" `
  --add-data="static;static" `
  --add-data="config;config" `
  --add-data=".env;." `
  app.py
