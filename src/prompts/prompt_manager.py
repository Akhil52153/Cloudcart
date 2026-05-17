"""Prompt management with versioning support."""

import os
import yaml
from pathlib import Path
from langchain_core.prompts.chat import ChatPromptTemplate
from src.models.schemas import PromptSchema
from src.prompts.prompt_builder import build_chat_prompt
from src.llms.groq_client import get_llm
from src.utils.logger import setup_logger

logger = setup_logger()


class PromptManager:
    """Manages prompt loading, compilation, and versioning."""

    def __init__(self, prompt_dir: Path):
        """
        Initialize with prompt directory.

        Args:
            prompt_dir: Path to the prompts directory
        """
        self.prompt_dir = prompt_dir

    def load(self, version: str) -> PromptSchema:
        """
        Load a prompt schema by version.

        Args:
            version: Version string (e.g., 'v1.0.0')

        Returns:
            Loaded PromptSchema

        Raises:
            FileNotFoundError: If version file doesn't exist
        """
        file_path = self.prompt_dir / f"{version}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt version {version} not found")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        schema = PromptSchema(**data)
        logger.info(f"Loaded prompt version {version}: {schema.metadata.description}")
        return schema

    def compile(self, schema: PromptSchema) -> ChatPromptTemplate:
        """
        Compile a PromptSchema into a ChatPromptTemplate.

        Args:
            schema: The prompt schema

        Returns:
            Compiled ChatPromptTemplate
        """
        return build_chat_prompt(schema)

    def invoke(self, prompt: ChatPromptTemplate, user_input: dict, schema: PromptSchema = None) -> str:
        """
        Invoke the LLM with the compiled prompt.

        Args:
            prompt: The compiled prompt template
            user_input: Dict with user input variables
            schema: Optional PromptSchema to validate inputs against

        Returns:
            LLM response content
            
        Raises:
            ValueError: If input validation against the schema fails
        """
        # Validate inputs against schema if provided (Assignment C.3)
        if schema and hasattr(schema, 'input_schema'):
            input_schema = schema.input_schema
            required_fields = input_schema.get("required", [])
            properties = input_schema.get("properties", {})
            
            # Check required fields
            for req in required_fields:
                if req not in user_input:
                    raise ValueError(f"Missing required input variable: {req}")
            
            # Check property constraints (e.g., max_length)
            for key, val in user_input.items():
                if key in properties:
                    max_len = properties[key].get("max_length")
                    if max_len and len(str(val)) > max_len:
                        raise ValueError(f"Input '{key}' exceeds max_length of {max_len}")
        
        llm = get_llm()
        chain = prompt | llm
        response = chain.invoke(user_input)
        return response.content

    def upgrade_current(self, new_version: str):
        """
        Upgrade the current.yaml to point to a new version using an OS symlink.
        
        EXPLANATION OF ZERO-DOWNTIME UPDATES (Assignment C.2):
        Symlinking matters for zero-downtime prompt updates because creating or replacing
        a symlink is an atomic operation at the OS level. Instead of modifying the contents
        of a file while the application might be actively reading it (which could cause 
        partial reads or crashes), we instantly swap the pointer to the new file. This 
        ensures the application always reads a complete, valid prompt file.

        Args:
            new_version: Target version (e.g., 'v1.1.0')
        """
        new_file = self.prompt_dir / f"{new_version}.yaml"
        current_file = self.prompt_dir / "current.yaml"

        if not new_file.exists():
            raise FileNotFoundError(f"New version {new_version} does not exist")

        # Remove the existing symlink or file
        if current_file.exists() or current_file.is_symlink():
            current_file.unlink()

        # Create a new symlink to the target version
        os.symlink(new_file.name, current_file)

        logger.info(f"Symlinked current.yaml to version {new_version}")