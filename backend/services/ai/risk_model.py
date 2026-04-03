"""
AEGISCORE — Risk Model Service
Random Forest classifier for per-file vulnerability risk prediction.
"""

import logging
import os
import pickle
from datetime import datetime, timezone
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

logger = logging.getLogger("aegiscore.risk_model")

FEATURE_NAMES = [
    "commit_frequency_30d",
    "author_count",
    "avg_diff_size",
    "past_vuln_count",
    "days_since_last_vuln",
    "file_complexity_score",
    "import_risk_score",
    "test_coverage_ratio",
]


class RiskModel:
    """
    Random Forest classifier for vulnerability risk prediction.
    Trained on organizational git history and scan findings.
    """

    def __init__(self, model_path: str):
        """
        Initialize the risk model.

        Args:
            model_path: Path to the pickled model file.
        """
        self.model_path = model_path
        self.model: RandomForestClassifier | None = None
        self._metadata: dict[str, Any] = {}

        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    saved = pickle.load(f)
                    if isinstance(saved, dict):
                        self.model = saved.get("model")
                        self._metadata = saved.get("metadata", {})
                    else:
                        self.model = saved
                logger.info(
                    "Loaded risk model from %s (version: %s)",
                    model_path,
                    self._metadata.get("model_version", "unknown"),
                )
            except (pickle.UnpicklingError, EOFError, KeyError) as e:
                logger.warning("Failed to load risk model: %s", e)
                self.model = None

    def train(self, training_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Train the Random Forest classifier on organizational data.

        Args:
            training_data: List of dicts, each containing:
                - Feature values (keys from FEATURE_NAMES)
                - 'had_vuln_next_scan' (bool): whether vulnerability appeared
                  in the next scan (label)

        Returns:
            Dictionary with precision, recall, f1_score, training_samples,
            and model_version.
        """
        if not training_data:
            raise ValueError("No training data provided")

        # Build feature matrix
        X = np.array([
            [float(sample.get(feat, 0.0)) for feat in FEATURE_NAMES]
            for sample in training_data
        ])
        y = np.array([
            1 if sample.get("had_vuln_next_scan", False) else 0
            for sample in training_data
        ])

        # Handle case where all labels are the same
        unique_labels = np.unique(y)
        if len(unique_labels) < 2:
            logger.warning(
                "Training data has only one class (%s). "
                "Model may not generalize well.",
                unique_labels[0],
            )

        # Split train/test
        if len(training_data) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if len(unique_labels) >= 2 else None,
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y

        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        zero_division_value = 0.0

        precision = float(precision_score(
            y_test, y_pred, zero_division=zero_division_value
        ))
        recall = float(recall_score(
            y_test, y_pred, zero_division=zero_division_value
        ))
        f1 = float(f1_score(
            y_test, y_pred, zero_division=zero_division_value
        ))

        # Generate model version
        model_version = datetime.now(timezone.utc).strftime("v%Y%m%d-%H%M%S")

        # Update metadata
        self._metadata = {
            "model_version": model_version,
            "last_trained_at": datetime.now(timezone.utc).isoformat(),
            "training_samples": len(training_data),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "feature_names": FEATURE_NAMES,
            "feature_importances": dict(zip(
                FEATURE_NAMES,
                [float(x) for x in self.model.feature_importances_],
            )),
            "scans_since_train": 0,
        }

        # Save to disk
        self._save()

        logger.info(
            "Model trained: version=%s samples=%d precision=%.3f recall=%.3f f1=%.3f",
            model_version,
            len(training_data),
            precision,
            recall,
            f1,
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "training_samples": len(training_data),
            "model_version": model_version,
        }

    def predict(self, features: dict[str, float]) -> float:
        """
        Predict vulnerability probability for a file.

        Args:
            features: Dictionary of feature values.

        Returns:
            Probability of vulnerability (0.0 to 1.0).
            Returns 0.5 if model is not trained (insufficient data signal).
        """
        if self.model is None:
            return 0.5

        try:
            feature_vector = np.array([
                [float(features.get(feat, 0.0)) for feat in FEATURE_NAMES]
            ])

            # Get probability of class 1 (vulnerable)
            probabilities = self.model.predict_proba(feature_vector)

            # Find index of class 1
            classes = list(self.model.classes_)
            if 1 in classes:
                vuln_idx = classes.index(1)
                return float(probabilities[0][vuln_idx])
            else:
                return 0.0

        except (ValueError, IndexError) as e:
            logger.warning("Prediction failed: %s", e)
            return 0.5

    def is_trained(self) -> bool:
        """Check if the model has been trained."""
        return self.model is not None

    def get_metadata(self) -> dict[str, Any]:
        """Get model metadata including version and accuracy metrics."""
        return self._metadata.copy()

    def increment_scan_count(self) -> int:
        """
        Increment the scan counter since last training.
        Returns the new count.
        """
        self._metadata["scans_since_train"] = (
            self._metadata.get("scans_since_train", 0) + 1
        )
        self._save()
        return self._metadata["scans_since_train"]

    def _save(self) -> None:
        """Save model and metadata to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(
                    {"model": self.model, "metadata": self._metadata},
                    f,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
        except OSError as e:
            logger.error("Failed to save model: %s", e)
