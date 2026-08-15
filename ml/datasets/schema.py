from pydantic import BaseModel, Field
from typing import Literal

class DatasetRow(BaseModel):
    sample_id: str = Field(..., min_length=1, description="Stable unique identifier for the sample")
    text: str = Field(..., min_length=1, description="The message or URL text")
    label: Literal["phishing", "benign"] = Field(..., description="Ground truth label")
    language: Literal["english", "hindi", "hinglish", "mixed_other"] = Field(..., description="Primary language of the text")
    script_type: Literal["latin", "devanagari", "mixed"] = Field(..., description="Writing script used")
    source_name: str = Field(..., min_length=1, description="Name of the source dataset or collection")
    source_type: Literal["public", "synthetic", "translated", "manual"] = Field(..., description="Provenance type of the data")
    split: Literal["train", "val", "test"] = Field(..., description="Strict dataset split assignment")
