from pydantic import BaseModel, Field


class NestedData(BaseModel):
    name: str
    value: int
    tags: list[str]


class PydanticParseParams(BaseModel):
    text: str = Field(default="test", description="Text to send")
    count: int = Field(default=5, ge=1, description="Count to send")
    nested: NestedData = Field(
        default_factory=lambda: NestedData(name="default", value=42, tags=["a", "b"])
    )


class TaskParams(BaseModel):
    duration: int = Field(
        default=10, ge=1, le=60, description="Duration of the task in seconds"
    )


class FailingTaskParams(BaseModel):
    error_message: str = Field(
        default="This is a deliberate error",
        description="Message to be raised in exception",
    )


class TaskOut(BaseModel):
    task_id: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    error: str | None = None


class MLInferenceParams(BaseModel):
    """Parameters for ML inference task."""

    model_id: str = Field(..., description="ID of the ML model to use for inference")
    input_data: dict = Field(..., description="Input data for the inference")


class MLTrainingParams(BaseModel):
    """Parameters for ML training task."""

    dataset_id: str = Field(..., description="ID of the dataset to use for training")
    model_configuration: dict = Field(..., description="Configuration for the ML model")
    hyperparameters: dict = Field(..., description="Hyperparameters for training")
