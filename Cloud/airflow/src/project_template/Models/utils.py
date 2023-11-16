import numpy as np
import warnings
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn
from mlflow.tracking.client import MlflowClient
from urllib.parse import urlparse
import time

import config

def track_run(run_name: str, estimator_name: str, hyperparams: dict, training_metrics: dict, validation_metrics: dict,
              model: any):
    # Auxiliar functions and connection stablishment
    client = MlflowClient(config.MLFLOW_ENDPOINT)
    mlflow.set_tracking_uri(config.MLFLOW_ENDPOINT)
    try:
        mlflow.set_experiment(config.MLFLOW_EXPERIMENT)
    except:
        time.sleep(10)
        mlflow.set_experiment(config.MLFLOW_EXPERIMENT)
    warnings.filterwarnings('ignore')

    mlflow.start_run(
        run_name=run_name,
        tags={'estimator_name': estimator_name}
    )

    active_run = mlflow.active_run()

    # track hypreparameters
    for key, value in hyperparams.items():
        mlflow.log_param(key, value)

    # Track training metrics
    for key, value in training_metrics.items():
        mlflow.log_metric(key, value)

    # Track validation metrics
    for key, value in validation_metrics.items():
        mlflow.log_metric(key, value)

    # Model registry
    tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
    if tracking_url_type_store != "file":
        mlflow.sklearn.log_model(model, "model", registered_model_name=run_name)
    else:
        mlflow.sklearn.log_model(model, "model")

    # End tracking
    mlflow.end_run()

    # Print report
    tr_keys = list(training_metrics.keys())
    tst_keys = list(validation_metrics.keys())

    print(f"{run_name}:")
    print("  TRAIN:")
    print("     Concordance index ipcw: %s" % training_metrics[tr_keys[0]])
    print("     Integrated Brier Score: %s" % training_metrics[tr_keys[1]])
    print("  VALIDATION:")
    print("     Concordance index ipcw: %s" % validation_metrics[tst_keys[0]])
    print("     Integrated Brier Score: %s" % validation_metrics[tst_keys[1]])
    print("     Mean AUC: %s" % validation_metrics[tst_keys[2]])

    # retur the run id
    return active_run