from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env.local'
load_dotenv(dotenv_path=env_path)
