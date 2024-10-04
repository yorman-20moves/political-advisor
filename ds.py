import os

print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir())
print("Contents of 'templates' directory (if it exists):", 
      os.listdir('templates') if os.path.exists('templates') else "No 'templates' directory found")