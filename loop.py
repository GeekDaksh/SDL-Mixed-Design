"""Expert review, the trial log, and the model update.

GENERATED FILE - do not edit. Edit 13_trial_loop_and_update.ipynb and re-run its export cell.

Eight outcomes, kept apart. Only MEASURED_WORKABILITY and MEASURED_STRENGTH
become training rows: a human rejection with no cast is not an observation.
One physical batch is one experimental unit, however many cubes it produced.
Validation levels are set here and nowhere else, and never by a model.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd

import is_rules as IS
import layer0 as L0
import workability_residual as WR

class Outcome(Enum):
    """What happened to a proposal. Trains the model only where stated."""

    HUMAN_REJECTED_BEFORE_CAST = "human_rejected_before_cast"
    MATERIAL_UNAVAILABLE = "material_unavailable"
    COST_REJECTED = "cost_rejected"
    CONSTRUCTABILITY_REJECTED = "constructability_rejected"
    OTHER_PROJECT_CONSTRAINT = "other_project_constraint"
    EXPERIMENT_FAILED = "experiment_failed"
    MEASURED_WORKABILITY = "measured_workability"
    MEASURED_STRENGTH = "measured_strength"


# [PC] The ONLY outcomes that may become numerical training observations.
TRAINING_OUTCOMES = frozenset({Outcome.MEASURED_WORKABILITY, Outcome.MEASURED_STRENGTH})


def trains_model(outcome) -> bool:
    """A human 'no' with no cast is not a data point. This is the enforcement."""
    return Outcome(outcome) in TRAINING_OUTCOMES


TRIAL_LOG_COLUMNS = [
    # identity
    "trial_id", "run_id", "plant_id", "state_hash", "proposed_at", "resolved_at",
    # the mix as designed
    "grade", "exposure", "use", "msa_mm", "cement_type", "slump_target_mm",
    "cement_kg_m3", "flyash_kg_m3", "ggbs_kg_m3", "water_kg_m3", "admixture_kg_m3",
    "binder_kg_m3", "fine_agg_kg_m3", "coarse_agg_kg_m3",
    "wb_ratio", "sp_pct_binder", "fine_frac_of_agg", "sand_zone",
    "target_mean", "S_used", "S_basis",
    # what the models said BEFORE the cast -- never overwritten
    "slump_pred", "slump_sd", "slump_lo90", "slump_hi90", "P_slump",
    "fc_pred", "fc_sd", "P_strength", "strength_status",
    # the code verdict
    "gate_pass", "gate_decided", "gate_hard_not_verified",
    "inside_training_range", "achievable_band",
    # what happened
    "outcome", "rejection_reason", "reviewer",
    "measured_slump_mm", "measured_fc_7d_mpa", "measured_fc_28d_mpa",
    "batch_id", "specimen_ids",
    # honesty
    "validation_level", "trains_model", "mode", "acquisition",
]


def new_trial_log() -> pd.DataFrame:
    return pd.DataFrame(columns=TRIAL_LOG_COLUMNS)


def log_proposals(batch, *, run_id, plant_id, req, state, mode, path="trial_log.csv"):
    """Write proposals to the log BEFORE any human sees them.

    Logging first is what makes a later rejection auditable: the prediction on record
    is the one the model made when it did not know the answer.
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for i, r in batch.reset_index(drop=True).iterrows():
        row = {c: None for c in TRIAL_LOG_COLUMNS}
        row.update({
            "trial_id": f"{run_id}-T{i+1}", "run_id": run_id, "plant_id": plant_id,
            "state_hash": r.get("state_hash"), "proposed_at": now,
            "grade": req.grade, "exposure": req.exposure.name, "use": req.use.name,
            "msa_mm": state.msa_mm, "cement_type": state.cement_type,
            "slump_target_mm": req.target_slump_mm,
            "validation_level": L0.ValidationLevel.COMPUTATIONALLY_COMPLIANT.name,
            "trains_model": False, "mode": mode,
            "acquisition": r.get("acquisition"),
        })
        for c in TRIAL_LOG_COLUMNS:
            if c in r and row.get(c) is None:
                row[c] = r[c]
        rows.append(row)

    df = pd.DataFrame(rows, columns=TRIAL_LOG_COLUMNS)
    p = Path(path)
    if p.exists():
        old = pd.read_csv(p)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(p, index=False)
    return df


def record_outcome(log, trial_id, outcome, *, reviewer=None, reason=None,
                   measured_slump_mm=None, measured_fc_7d=None, measured_fc_28d=None,
                   batch_id=None, specimen_ids=None, path="trial_log.csv"):
    """Record what happened. Refuses to file a measurement without a value, and
    refuses to promote a validation level without a measurement behind it."""
    outcome = Outcome(outcome)
    i = log.index[log["trial_id"] == trial_id]
    if len(i) != 1:
        raise KeyError(f"trial_id {trial_id!r} matched {len(i)} rows")
    i = i[0]

    if outcome is Outcome.MEASURED_WORKABILITY and measured_slump_mm is None:
        raise ValueError("MEASURED_WORKABILITY needs a measured slump")
    if outcome is Outcome.MEASURED_STRENGTH and measured_fc_28d is None:
        raise ValueError("MEASURED_STRENGTH needs a measured 28-day strength")
    if outcome not in TRAINING_OUTCOMES and any(
            v is not None for v in (measured_slump_mm, measured_fc_7d, measured_fc_28d)):
        raise ValueError(
            f"{outcome.name} carries measurements. If something was cast and measured, "
            f"the outcome is a MEASURED_* one. Record the rejection separately."
        )
    if outcome is not Outcome.HUMAN_REJECTED_BEFORE_CAST and outcome not in TRAINING_OUTCOMES \
            and outcome is not Outcome.EXPERIMENT_FAILED and not reason:
        raise ValueError(f"{outcome.name} must record a reason")

    log.loc[i, "outcome"] = outcome.value
    log.loc[i, "reviewer"] = reviewer
    log.loc[i, "rejection_reason"] = reason
    log.loc[i, "resolved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.loc[i, "measured_slump_mm"] = measured_slump_mm
    log.loc[i, "measured_fc_7d_mpa"] = measured_fc_7d
    log.loc[i, "measured_fc_28d_mpa"] = measured_fc_28d
    log.loc[i, "batch_id"] = batch_id
    log.loc[i, "specimen_ids"] = ";".join(map(str, specimen_ids)) if specimen_ids else None
    log.loc[i, "trains_model"] = trains_model(outcome)

    if outcome in TRAINING_OUTCOMES:
        log.loc[i, "validation_level"] = L0.ValidationLevel.LAB_VALIDATED.name
    # TRIAL_BATCH_VALIDATED and PRODUCTION_VALIDATED are promoted by promote(), which
    # requires plant evidence -- never by a measurement alone.

    log.to_csv(path, index=False)
    return log


def promote(log, trial_id, level, *, evidence, path="trial_log.csv"):
    """[PC] Raise a validation level. Requires written evidence, always."""
    level = L0.ValidationLevel(level) if not isinstance(level, L0.ValidationLevel) else level
    if not evidence:
        raise ValueError("a validation level may not be raised without recorded evidence")
    i = log.index[log["trial_id"] == trial_id][0]
    cur = L0.ValidationLevel[log.loc[i, "validation_level"]]
    if level.value != cur.value + 1:
        raise ValueError(f"levels are climbed one at a time: {cur.name} -> {level.name}")
    if cur is L0.ValidationLevel.COMPUTATIONALLY_COMPLIANT and not log.loc[i, "trains_model"]:
        raise ValueError("cannot reach LAB_VALIDATED without a measured result behind it")
    log.loc[i, "validation_level"] = level.name
    log.loc[i, "rejection_reason"] = f"{log.loc[i, 'rejection_reason'] or ''}|promoted: {evidence}".strip("|")
    log.to_csv(path, index=False)
    return log


def training_rows(log, kind="workability"):
    """Extract trainable rows. Group key = the physical batch, not the specimen."""
    want = (Outcome.MEASURED_WORKABILITY if kind == "workability"
            else Outcome.MEASURED_STRENGTH)
    df = log[log["outcome"] == want.value].copy()
    if df.empty:
        return df
    # [PC] one physical batch = one experimental unit
    df["design_grp"] = df["batch_id"].fillna(df["trial_id"])
    if kind == "workability":
        df["slump_mm"] = pd.to_numeric(df["measured_slump_mm"], errors="coerce")
        df = df.dropna(subset=["slump_mm"])
    else:
        df["fc_28d"] = pd.to_numeric(df["measured_fc_28d_mpa"], errors="coerce")
        df = df.dropna(subset=["fc_28d"])
    return df


def independent_conditions(df, group_col="design_grp") -> int:
    """The number that goes in the report. Not the row count."""
    return int(df[group_col].nunique()) if len(df) else 0


def prediction_error_report(log):
    """What the model said before the cast, against what came back. Never overwritten."""
    d = log[log["outcome"] == Outcome.MEASURED_WORKABILITY.value].copy()
    if d.empty:
        return pd.DataFrame()
    d["measured_slump_mm"] = pd.to_numeric(d["measured_slump_mm"], errors="coerce")
    d["slump_pred"] = pd.to_numeric(d["slump_pred"], errors="coerce")
    d = d.dropna(subset=["measured_slump_mm", "slump_pred"])
    d["error_mm"] = d["slump_pred"] - d["measured_slump_mm"]
    d["inside_90"] = ((d["measured_slump_mm"] >= pd.to_numeric(d["slump_lo90"], errors="coerce")) &
                      (d["measured_slump_mm"] <= pd.to_numeric(d["slump_hi90"], errors="coerce")))
    return d[["trial_id", "slump_pred", "slump_lo90", "slump_hi90",
              "measured_slump_mm", "error_mm", "inside_90"]]


def plant_tau(log, plant_id):
    """[PC] Plant offset tau: the systematic slump bias at one plant, in mm.

    Estimated only from that plant's MEASURED rows. It is an offset, not a rescaling,
    and it is applied to the prediction, never folded into the training target -- so a
    later refit is not contaminated by it.
    """
    d = log[(log["plant_id"] == plant_id) &
            (log["outcome"] == Outcome.MEASURED_WORKABILITY.value)].copy()
    d["measured_slump_mm"] = pd.to_numeric(d["measured_slump_mm"], errors="coerce")
    d["slump_pred"] = pd.to_numeric(d["slump_pred"], errors="coerce")
    d = d.dropna(subset=["measured_slump_mm", "slump_pred"])
    n_groups = independent_conditions(d.assign(design_grp=d["batch_id"].fillna(d["trial_id"])))
    if n_groups < 3:
        return {"plant_id": plant_id, "tau_mm": None, "n_groups": n_groups,
                "status": "NOT_VERIFIED -- fewer than 3 independent batches at this plant"}
    resid = (d["measured_slump_mm"] - d["slump_pred"]).to_numpy(float)
    return {"plant_id": plant_id, "tau_mm": float(np.mean(resid)),
            "sd_mm": float(np.std(resid, ddof=1)), "n_groups": n_groups,
            "status": "estimated"}


def refit_needed(log, wmodel, *, min_new_groups=2):
    """[PC] When is a refit worth running? When enough NEW independent batches exist."""
    tr = training_rows(log, "workability")
    have = set(map(str, wmodel.get("trained_on_groups", [])))
    new = set(map(str, tr["design_grp"].unique())) - have if len(tr) else set()
    return {"new_groups": sorted(new), "n_new": len(new),
            "refit": len(new) >= min_new_groups,
            "rule": f"[PC] refit once {min_new_groups} new independent batches exist"}
