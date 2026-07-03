# Reflection (≤1 page)

Fill this in before you submit.

**Which fault types were hardest to catch, and why?**

Subtle anomalies (specifically lineage runtime duration anomalies and subtle embedding/corpus staleness drifts) were the hardest to catch. The subtle lineage runtimes (ranging between 4400ms and 4700ms) overlapped significantly with normal variance in clean runs (which peaked up to 4805ms). Embedding drift and corpus staleness subtle anomalies also lie well within the baseline parameters, requiring highly calibrated thresholds to catch faults while avoiding false alarms.

**What would you change about your cost/coverage tradeoff, if you had another pass?**

Since the private phase budget (320.0 credits) is sufficient to profile all 200 events exactly once (costing 300.0 credits), we did not need to skip any tool calls to avoid overage. If we had another pass with a tighter budget constraint, we would store running metrics in `ctx.state` to build a dynamic baseline and prioritize profiling components showing high historical variance, or dynamically scale back tool calls when budget is low.

