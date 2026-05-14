# ============================================================================
# ModelServe — MLflow Model Loader
# ============================================================================

import os
from typing import Any, Optional

import mlflow
import pandas as pd

from logger import get_logger


logger = get_logger(__name__)


class ModelLoader:
    def __init__(self, mlflow_tracking_uri: str, model_name: str) -> None:
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.model_name = model_name
        self._model: Optional[Any] = None
        self._version: Optional[str] = None

        self._load_model()

    def _load_model(self) -> None:
        try:
            mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            model_alias = os.environ.get("MODEL_ALIAS")
            model_stage = os.environ.get("MODEL_STAGE")

            if model_alias or not model_stage:
                model_alias = model_alias or "production"
                model_uri = f"models:/{self.model_name}@{model_alias}"
            else:
                model_uri = f"models:/{self.model_name}/{model_stage}"

            self._model = mlflow.pyfunc.load_model(model_uri)

            client = mlflow.MlflowClient()
            if model_alias:
                model_version = client.get_model_version_by_alias(self.model_name, model_alias)
                self._version = str(model_version.version)
            elif model_stage:
                latest_version = client.get_latest_versions(self.model_name, stages=[model_stage])
                self._version = str(latest_version[0].version) if latest_version else "unknown"
            else:
                self._version = "unknown"

            logger.info("Successfully loaded model '%s' version %s", self.model_name, self._version)
        except Exception as e:
            logger.error("Failed to load model from MLflow: %s", e)
            self._model = None
            self._version = None

    def predict(self, features: pd.DataFrame) -> Any:
        if self._model is None:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        return self._model.predict(features)

    def get_version(self) -> Optional[str]:
        return self._version
