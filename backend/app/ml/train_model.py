"""Isolation Forest Model Training Script.

Trains an unsupervised Isolation Forest model on normal baseline API traffic patterns.
Saves the serialized model artifact using joblib for production gateway inference.
"""

import os
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest
from app.ml.feature_engineering import generate_synthetic_baseline, FEATURE_NAMES
from app.core.config import settings
from app.utils.logger import logger


def get_default_model_path() -> Path:
    """Resolve absolute path to the model destination file."""
    # Find base backend directory
    base_dir = Path(__file__).resolve().parent.parent.parent
    target_path = base_dir / settings.MODEL_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return target_path


def train_isolation_forest(
    n_samples: int = 2000,
    contamination: float = 0.03,
    random_state: int = 42,
    save_path: Path | None = None,
) -> IsolationForest:
    """Generate synthetic baseline traffic, train Isolation Forest, and persist model."""
    logger.info(f"Generating {n_samples} baseline normal traffic windows for training...")
    df_train = generate_synthetic_baseline(n_samples=n_samples, random_state=random_state)

    logger.info(f"Training IsolationForest (contamination={contamination}, random_state={random_state})...")
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )

    model.fit(df_train[FEATURE_NAMES])

    destination = save_path or get_default_model_path()
    joblib.dump(model, destination)
    logger.info(f"Successfully trained and saved model artifact to {destination}")

    return model


if __name__ == "__main__":
    train_isolation_forest()
