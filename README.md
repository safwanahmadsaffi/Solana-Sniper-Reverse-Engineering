# Solana Sniper Bot Reverse-Engineering & Replica Strategy

This repository contains the complete reverse-engineering analysis, machine learning models, data visualizations, and execution scripts for decoding and replicating the on-chain Solana sniper bot (`5brv79eFZ2rGprXNvqgVJBkBptkkw8GJX1XydJyZLyAr`) operating on `pump.fun`.

## Repository Structure

- `writeup_deep_analysis.md`: Detailed research report explaining the discovery of the bot's creator-following selection logic.
- `risk_analysis.md`: Comprehensive risk assessment covering mempool competition, MEV hazards, smart contract risks, and capital preservation.
- `replica_strategy_v2.py`: Optimized, low-latency Python inference script utilizing pre-calculated rolling creator profiles and XGBoost scoring.
- `feature_importance.png`: Visual chart illustrating feature weights in the replica model.
- `historical_win_rate_dist.png`: KDE distribution plot contrasting creator win rates for sniped vs. non-sniped tokens.

---

## Getting Started & Execution Instructions

### Prerequisites
Ensure you have Python 3.10+ installed along with the required machine learning and data processing libraries:

```bash
pip install xgboost pandas numpy scikit-learn pyarrow
```

### Running the Replica Strategy
To execute the optimized inference and evaluation pipeline:

```bash
python3 replica_strategy_v2.py
```

The script loads deployer transaction history, computes rolling features (`historical_win_rate`, `cum_launches`, `time_since_last_launch`), scores new token deployments in real-time, and outputs model performance metrics.

---
**Author**: Manus AI
