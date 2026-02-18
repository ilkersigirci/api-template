from pydantic import BaseModel, Field

ML_INFERENCE_TASK = "ml_inference"
TRAIN_MODEL_TASK = "train_model"


class MLInferenceInput(BaseModel):
    model_id: str = Field(..., description="ID of the ML model to use for inference")
    input_data: dict = Field(
        ...,
        description="Input data with 'features' and optional 'num_classes'",
        examples=[{"features": [1.0, 2.0, 3.0], "num_classes": 3}],
    )


class MLInferenceResult(BaseModel):
    model_id: str
    predictions: list[float]
    confidence: float


class MLTrainingInput(BaseModel):
    dataset_id: str = Field(..., description="ID of the dataset to use for training")
    model_configuration: dict = Field(
        ...,
        description="Model config with 'input_size' and 'output_size'",
        examples=[{"input_size": 10, "output_size": 1}],
    )
    hyperparameters: dict = Field(
        ...,
        description="Training hyperparameters: epochs, learning_rate, batch_size",
        examples=[{"epochs": 5, "learning_rate": 0.01, "batch_size": 32}],
    )


class MLTrainingResult(BaseModel):
    dataset_id: str
    model_id: str
    training_metrics: dict[str, float | int]
