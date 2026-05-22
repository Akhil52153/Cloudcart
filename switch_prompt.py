from pathlib import Path
from src.prompts.prompt_manager import PromptManager

pm = PromptManager(Path("prompts/cloudcart"))

pm.upgrade_current("v1.1.0")

print("Switched current.yaml to v1.1.0")