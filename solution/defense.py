"""
Your defense. Implement register(ctx) and a handler per event type.
See ../README.md for the full interface + toolkit reference, and
../RULES.md before you start.
"""
from api import Verdict


def register(ctx):
    ctx.on("data_batch", check_data_batch)
    ctx.on("contract_checkpoint", check_contract_checkpoint)
    ctx.on("lineage_run", check_lineage_run)
    ctx.on("feature_materialization", check_feature_materialization)
    ctx.on("embedding_batch", check_embedding_batch)


def check_data_batch(payload, ctx):
    profile = ctx.tools.batch_profile(payload["batch_id"])
    if "error" in profile:
        return Verdict(alert=False, pillar="checks", reason=profile["error"])
    
    alert = False
    reasons = []
    
    # 1. Volume checks (row_count)
    if profile["row_count"] < 445.4732 or profile["row_count"] > 591.2948:
        alert = True
        reasons.append("row_count_out_of_bounds")
        
    # 2. Null rate checks
    null_rate = profile["null_rate"].get("customer_id", 0.0)
    if null_rate > 0.0075:
        alert = True
        reasons.append("null_rate_too_high")
        
    # 3. Mean amount checks
    if profile["mean_amount"] < 76.7645 or profile["mean_amount"] > 84.6053:
        alert = True
        reasons.append("mean_amount_out_of_bounds")
        
    # 4. Staleness checks
    if profile["staleness_min"] > 6.0:
        alert = True
        reasons.append("staleness_too_high")
        
    return Verdict(alert=alert, pillar="checks", reason=", ".join(reasons))


def check_contract_checkpoint(payload, ctx):
    diff = ctx.tools.contract_diff(payload["contract_id"], payload["checkpoint_batch_id"])
    if "error" in diff:
        return Verdict(alert=False, pillar="contracts", reason=diff["error"])
        
    alert = False
    reasons = []
    
    # 1. Schema or type violations returned by the tool
    violations = diff.get("violations", [])
    if len(violations) > 0:
        alert = True
        reasons.extend(violations)
        
    # 2. Freshness SLA check (declared_sla in payload)
    sla = payload.get("declared_sla", {})
    freshness_limit = sla.get("freshness_min", 999999)
    if diff["freshness_delay_min"] > freshness_limit:
        alert = True
        reasons.append(f"freshness_delay_{diff['freshness_delay_min']:.2f}_exceeds_sla_{freshness_limit}")
        
    return Verdict(alert=alert, pillar="contracts", reason=", ".join(reasons))


def check_lineage_run(payload, ctx):
    slice_info = ctx.tools.lineage_graph_slice(payload["run_id"])
    if "error" in slice_info:
        return Verdict(alert=False, pillar="lineage", reason=slice_info["error"])
        
    alert = False
    reasons = []
    
    # 1. Duration check
    if slice_info["duration_ms"] > 4420:
        alert = True
        reasons.append("duration_too_high")
        
    # 2. Orphan output check
    if slice_info["actual_downstream_count"] == 0:
        alert = True
        reasons.append("orphan_output")
        
    # 3. Upstream checklist
    expected_upstreams = ["raw.orders", "raw.customers"]
    actual_upstreams = slice_info.get("actual_upstream", [])
    if not all(u in actual_upstreams for u in expected_upstreams):
        alert = True
        reasons.append("missing_upstream")
        
    return Verdict(alert=alert, pillar="lineage", reason=", ".join(reasons))


def check_feature_materialization(payload, ctx):
    drift = ctx.tools.feature_drift(payload["feature_view"], payload["batch_id"])
    if "error" in drift:
        return Verdict(alert=False, pillar="ai_infra", reason=drift["error"])
        
    alert = False
    reasons = []
    
    if drift["mean_shift_sigma"] > 0.30:
        alert = True
        reasons.append("feature_drift_exceeded")
        
    return Verdict(alert=alert, pillar="ai_infra", reason=", ".join(reasons))


def check_embedding_batch(payload, ctx):
    drift = ctx.tools.embedding_drift(payload["corpus"], payload["chunk_batch_id"])
    if "error" in drift:
        return Verdict(alert=False, pillar="ai_infra", reason=drift["error"])
        
    alert = False
    reasons = []
    
    if drift["centroid_shift"] > 0.028:
        alert = True
        reasons.append("centroid_drift_exceeded")
    if drift["avg_doc_age_days"] > 30.5:
        alert = True
        reasons.append("staleness_exceeded")
        
    return Verdict(alert=alert, pillar="ai_infra", reason=", ".join(reasons))

