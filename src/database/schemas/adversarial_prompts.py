from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AdversarialPrompt(BaseModel):
    source_dataset: str = Field(..., description="Identifier for the original dataset (e.g., 'bipia', 'tensortrust').")
    source_file: str = Field(..., description="The specific file the record came from.")
    raw_record_id: Optional[str] = Field(None, description="An ID from the original dataset, if available.")
    split: Optional[str] = Field(None, description="The original dataset split (e.g., 'train', 'Phase1').")
    attack_type: Optional[str] = Field(None, description="Category of attack (e.g., 'prompt_injection', 'jailbreak', 'red_teaming').")
    domain: Optional[str] = Field(None, description="Application area (e.g., 'email', 'code', 'game').")
    prompt: str = Field(..., description="The complete text passed to the model. This may be a composite of several fields from the raw data.")
    prompt_components: Optional[Dict[str, Any]] = Field(None, description="For composite prompts, a key-value store of the original pieces (e.g., {'pre_prompt': '...', 'attack_input': '...', 'post_prompt': '...'}).")
    user_task: Optional[str] = Field(None, description="The intended benign task, if specified.")
    expected_output: Optional[str] = Field(None, description="The ground-truth or ideal string response.")
    attack_objectives: Optional[Dict[str, Any]] = Field(None, description="A structured representation of the attack's goals and outcomes.")
    is_adversarial: bool = Field(..., description="A flag indicating if the record is an attack or a benign example.")
    raw_record_link: str = Field(..., description="The _id of the original record in its raw collection.")
