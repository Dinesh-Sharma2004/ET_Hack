# MLflow usage

- Track recommendation experiments by `experiment_id`.
- Log retriever variants, embedding model version, and prompt version.
- Store offline metrics:
  - precision@k
  - recall@k
  - CTR uplift
  - dwell time uplift
- Promote winning models only after online A/B validation.
