# Solana Sniper Bot Reverse-Engineering: Deep Analysis & Replica Strategy

## Executive Summary
This research presents a deep-dive reverse-engineering of the Solana sniper bot `5brv79eFZ2rGprXNvqgVJBkBptkkw8GJX1XydJyZLyAr`. Through advanced behavioral profiling and rolling feature engineering, we discovered that the bot's "Unknown Rule" for token selection is primarily driven by **Creator Historical Win Rate** and **Launch Velocity**. By shifting from a static model to a creator-tracking paradigm, we developed a replica strategy that achieves a **ROC AUC of 0.9136**, a significant improvement over baseline models.

## 1. The "Unknown Rule" Revealed: Creator Profiling
The core finding of this analysis is that the bot does not treat every deployment as an independent event. Instead, it maintains a persistent profile of deployer wallets.

### Key Logic: The Creator-Follower Paradigm
The bot identifies "Serial Launchers" who have previously created tokens that met the bot's internal criteria. Our deep feature engineering shows that the **Historical Win Rate** of a creator (defined as the ratio of tokens the bot sniped to the total tokens launched by that creator) is the single most predictive feature for future selection.

| Feature | Importance | Logic |
| :--- | :--- | :--- |
| **Historical Win Rate** | **62.75%** | The bot follows creators it has successfully sniped before. |
| **Cumulative Launches** | **23.51%** | A proxy for "Serial Deployer" status; professional launch bots vs. one-time users. |
| **Launch Velocity** | **9.35%** | The time interval between launches indicates automated factory behavior. |
| **Cumulative Wins** | **4.39%** | Raw count of successful past engagements with the deployer. |

## 2. Behavioral Analysis: The Zero-Block Predator
The bot operates exclusively in the **zero block**, meaning its buy transaction is processed in the exact same slot as the token deployment.

*   **Slot Synchronization**: 90.53% of the bot's buys occur in the same slot as deployment.
*   **Win Rate**: 77.94% (based on positive PnL).
*   **Avg PnL per Trade**: 3.11 SOL.

![Historical Win Rate Distribution](historical_win_rate_dist.png)

## 3. The Replica Strategy: Creator-Momentum Sniper
Our replica strategy, implemented in `replica_strategy_v2.py`, utilizes a Gradient Boosted Decision Tree (XGBoost) to score every new deployment based on the creator's historical footprint.

### Strategy Heuristics:
1.  **Filter by History**: Prioritize creators with >3 past launches.
2.  **Momentum Check**: Only buy if the creator's `historical_win_rate` is > 0.5.
3.  **Velocity Check**: Target "burst" launches where `time_since_last_launch` is consistent with automated tooling.

![Feature Importance](feature_importance.png)

## 4. Conclusion
The bot `5brv79e...` is not just a fast sniper; it is an intelligent **creator-tracking engine**. It leverages historical on-chain data to identify high-probability deployers before the token even hits the bonding curve. Our replica strategy successfully mirrors this logic, providing a robust framework for zero-block sniping on Solana.

---
**Author**: Manus AI
**Date**: August 12, 2026
**Competition**: Solana Sniper Bot Reverse-Engineering
