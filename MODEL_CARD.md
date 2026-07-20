# Hardness Prediction Model Card

## Intended use

The bundled model predicts Vickers hardness (`HV`) for high-entropy alloy
compositions. It is intended for research screening and platform demonstration,
not as a substitute for experimental measurement, engineering qualification,
or a safety decision.

## Inputs and output

- Supported elements: `Al`, `Co`, `Cr`, `Cu`, `Fe`, `Hf`, `Mn`, `Mo`, `Nb`,
  `Ni`, `Ta`, `Ti`, `V`, `W`, and `Zr`.
- Each element value must be between 0 and 100 and the supplied total must be
  greater than zero.
- Values may be fractions or percentages; inference normalises the
  composition.
- Output: predicted Vickers hardness, `Pred_HV`.

## Implementation

- Serialized pipeline: scikit-learn `Pipeline` containing a `MinMaxScaler` and
  `GaussianProcessRegressor`.
- Serialization stack: CPython 3.8.19, NumPy 1.24.4, SciPy 1.10.1,
  pandas 1.2.4, scikit-learn 1.3.2, and joblib 1.4.2.
- Feature workflow: 182 candidate descriptors are calculated from composition
  and elemental parameter tables; the deployed artifact uses 12 selected
  features.
- Training table: 455 data rows and 17 columns, including the alloy label,
  15 element columns, and measured hardness.

## Artifact integrity

SHA-256 checksums:

```text
ECB7859130351E16B44AA9E1DA9B65B924D6559098BAC12A16B857242072A883  HV-Prediction/outputs/model_20260320_062441/Best_HV_pipeline.pkl
67B068AD0D217302405E3C6B5902A5DB879D3FC7897ACBD00FAA25D2E506A078  HV-Prediction/outputs/model_20260320_062441/Best_model_HV.pkl
38E0CB8529AD48131A21A894A447941246F9DD0E213F340F290C0CA428CAEEDB  HV-Prediction/Data/HV-Data.xlsx
BFA9543992EFF3377B2CF99DC5A4DD051F99034F4BC29399C0DE19658F1A8141  HV-Prediction/Data/Element_info.csv
8A0345EF67278DB8F4501A8DC80167250EE4341FB4EB0A8B7DF5988E87AC3719  HV-Prediction/Data/Enthalpy_data.csv
```

Do not replace a joblib/pickle artifact with a file from an untrusted source.

## Limitations

- Accuracy outside the chemical domain represented by the training set has not
  been established.
- The API returns a point prediction and does not expose a calibrated
  uncertainty interval.
- Missing elements are interpreted as zero; users must verify composition and
  units before prediction.
- The legacy `F*` descriptor implementation uses the complete input matrix as
  context. Consequently, a sample submitted through the batch endpoint can
  receive a different value from the same composition submitted alone. Use the
  single-sample endpoint for results comparable with the current user interface.
  Correcting this fitted transformation requires model retraining and validation.
- Model output should be independently validated against experiments.
- The repository does not currently include a publication-ready provenance and
  redistribution statement for every source row. Add this information before
  archival publication.

## Reproducibility

Install `requirements-training.txt` and run `HV-Prediction/train.py` from the
`HV-Prediction` directory. The existing training script uses a fixed split seed,
but hyperparameter optimisation is not guaranteed to reproduce an identical
binary artifact across platforms or repeated runs.
