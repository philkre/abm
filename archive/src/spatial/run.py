"""Run the spatial threshold PGG and save results to data/."""

from pathlib import Path

from joblib import dump

from spatial.config import DEFAULT_CONFIG
from spatial.model import SpatialCollectiveRiskModel

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def main() -> None:
    cfg = DEFAULT_CONFIG
    model = SpatialCollectiveRiskModel(cfg)

    for _ in range(cfg.n_steps):
        model.step()

    df = model.datacollector.get_model_vars_dataframe()

    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / "spatial_tpgg.pkl"
    dump(df, out_path)
    print(f"Saved results to {out_path}")
    print(df.tail(5))


if __name__ == "__main__":
    main()
