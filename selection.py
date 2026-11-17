"""Selection - SERVE ranks feasible mixes, EXPLORE proposes trials.

GENERATED FILE - do not edit. Edit 12_select_serve_explore.ipynb and re-run its export cell.

SERVE hard-rejects anything outside training support and ranks on cost and carbon.
EXPLORE keeps and flags such points, because that is where a trial teaches most.
Standards constraints are identical in both. Bayesian optimisation is a PROJECT
RESEARCH METHOD, not an Indian Standard requirement.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from dataclasses import replace as _replace

import is_rules as IS
import layer0 as L0
import screen as SC
import workability_residual as WR

class ValueStatus:
    """[PC] Where a rate or factor came from. Printed on every ranked output."""

    MEASURED = "measured"        # from this plant
    PUBLISHED = "published"      # a citable Indian source or EPD
    PLACEHOLDER = "placeholder"  # neither -- must be surfaced on every output


# [PC] PLACEHOLDER rates. These are NOT measured and NOT published. They exist so the
#      ranking machinery can be tested; any portfolio ranked on them says so on its face.
#      Replace with plant rates (MEASURED) or an Indian EPD (PUBLISHED) before use.
RATES_INR_PER_KG = {
    "cement": (8.00, ValueStatus.PLACEHOLDER),
    "flyash": (2.50, ValueStatus.PLACEHOLDER),
    "ggbs": (4.50, ValueStatus.PLACEHOLDER),
    "water": (0.05, ValueStatus.PLACEHOLDER),
    "admixture": (95.00, ValueStatus.PLACEHOLDER),
    "coarse_agg": (1.20, ValueStatus.PLACEHOLDER),
    "fine_agg": (1.60, ValueStatus.PLACEHOLDER),
}

CARBON_KG_PER_KG = {
    "cement": (0.90, ValueStatus.PLACEHOLDER),
    "flyash": (0.02, ValueStatus.PLACEHOLDER),
    "ggbs": (0.08, ValueStatus.PLACEHOLDER),
    "water": (0.00, ValueStatus.PLACEHOLDER),
    "admixture": (1.50, ValueStatus.PLACEHOLDER),
    "coarse_agg": (0.01, ValueStatus.PLACEHOLDER),
    "fine_agg": (0.01, ValueStatus.PLACEHOLDER),
}

_COLS = {"cement": "cement_kg_m3", "flyash": "flyash_kg_m3", "ggbs": "ggbs_kg_m3",
         "water": "water_kg_m3", "admixture": "admixture_kg_m3",
         "coarse_agg": "coarse_agg_kg_m3", "fine_agg": "fine_agg_kg_m3"}

_WORST = [ValueStatus.MEASURED, ValueStatus.PUBLISHED, ValueStatus.PLACEHOLDER]


def price_and_carbon(df, rates=None, carbon=None):
    """Cost and carbon per m3, each carrying the worst status of its constituents."""
    rates = rates or RATES_INR_PER_KG
    carbon = carbon or CARBON_KG_PER_KG
    out = df.copy()

    cost = np.zeros(len(out))
    co2 = np.zeros(len(out))
    cost_status, co2_status = ValueStatus.MEASURED, ValueStatus.MEASURED
    for key, col in _COLS.items():
        if col not in out:
            continue
        r, rs = rates[key]
        c, cs = carbon[key]
        cost += out[col].to_numpy(float) * r
        co2 += out[col].to_numpy(float) * c
        cost_status = max(cost_status, rs, key=_WORST.index)
        co2_status = max(co2_status, cs, key=_WORST.index)

    out["cost_inr_m3"] = cost
    out["carbon_kg_m3"] = co2
    out["cost_status"] = cost_status
    out["carbon_status"] = co2_status
    return out


def pareto_front(df, objectives=("cost_inr_m3", "carbon_kg_m3"), minimise=True):
    """[PC] Non-dominated rows. No weights, because no exchange rate has been agreed."""
    X = df[list(objectives)].to_numpy(float)
    if not minimise:
        X = -X
    keep = np.ones(len(X), dtype=bool)
    for i in range(len(X)):
        if not keep[i]:
            continue
        dominated = np.all(X <= X[i], axis=1) & np.any(X < X[i], axis=1)
        if dominated.any():
            keep[i] = False
    return df[keep].copy()


def rank_serve(cands, *, p_strength_min=0.90, p_slump_min=0.80, rates=None, carbon=None,
               front_only=True):
    """[PC] SERVE: feasible, code-decided, inside support, then ranked on cost and carbon.

    Raises rather than ranking around a NaN P_strength. A candidate whose strength
    cannot be predicted is NOT_VERIFIED, and the project's fail-safe rule forbids
    substituting an optimistic number for it.
    """
    if cands.empty:
        return cands.copy(), {"n_in": 0, "n_feasible": 0, "reason": "no candidates"}

    if "P_strength" in cands and cands["P_strength"].isna().any():
        n = int(cands["P_strength"].isna().sum())
        raise ValueError(
            f"{n} of {len(cands)} candidates have P_strength = NaN "
            f"(strength_status: {sorted(set(cands.get('strength_status', ['?'])))}). "
            f"A NOT_VERIFIED hard check may not be ranked around. Load a strength model, "
            f"or use the verified deterministic procedure, or refuse the order."
        )

    df = price_and_carbon(cands, rates, carbon)
    reasons = {}
    m = df["gate_decided"].astype(bool)
    reasons["gate not decided"] = int((~m).sum())
    if "inside_training_range" in df:
        m2 = df["inside_training_range"] != False
        reasons["outside training support"] = int((~m2).sum())
        m &= m2
    m3 = df["P_strength"] >= p_strength_min
    reasons[f"P_strength < {p_strength_min}"] = int((~m3).sum())
    m &= m3
    m4 = df["P_slump"] >= p_slump_min
    reasons[f"P_slump < {p_slump_min}"] = int((~m4).sum())
    m &= m4

    feasible = df[m].copy()
    meta = {"n_in": len(df), "n_feasible": len(feasible), "excluded": reasons,
            "cost_status": df["cost_status"].iloc[0],
            "carbon_status": df["carbon_status"].iloc[0],
            "thresholds": {"p_strength_min": p_strength_min, "p_slump_min": p_slump_min}}
    if feasible.empty:
        return feasible, meta

    ranked = pareto_front(feasible) if front_only else feasible
    ranked = ranked.sort_values(["cost_inr_m3", "carbon_kg_m3"]).reset_index(drop=True)
    meta["n_ranked"] = len(ranked)
    return ranked, meta


def acquisition_uncertainty(df, *, sd_col="slump_sd", feas_cols=("P_strength", "P_slump"),
                            feas_floor=0.05):
    """[BO] Score = predictive sd, weighted by how feasible the point still is.

    Deliberately simple and fully documented. NO CLAIM is made that this beats qNEHVI,
    qEI or any alternative; that needs a comparison this project has not run, and with
    five independent design families it would not be conclusive either way.

    A point with near-zero feasibility is not informative about a mix anyone would cast,
    so it is down-weighted rather than chased.
    """
    sd = df[sd_col].to_numpy(float)
    w = np.ones(len(df))
    for c in feas_cols:
        if c in df:
            w = w * np.clip(np.nan_to_num(df[c].to_numpy(float), nan=feas_floor),
                            feas_floor, 1.0)
    return sd * w


def propose_batch(cands, k=4, *, design_cols=("dv_binder_kg_m3", "dv_flyash_frac",
                                              "dv_ggbs_frac", "dv_sp_pct_binder"),
                  diversity_weight=1.0, sd_col="slump_sd"):
    """[BO] Greedy batch with a diversity penalty, so k trials are not k copies.

    Returns (batch, meta). meta carries the joint batch risk.
    """
    if cands.empty:
        return cands.copy(), {"k": 0, "reason": "no candidates"}
    df = cands.copy().reset_index(drop=True)
    score = acquisition_uncertainty(df, sd_col=sd_col)

    cols = [c for c in design_cols if c in df]
    X = df[cols].to_numpy(float)
    rng = X.max(axis=0) - X.min(axis=0)
    rng[rng == 0] = 1.0
    Xn = (X - X.min(axis=0)) / rng

    chosen = []
    for _ in range(min(k, len(df))):
        s = score.copy()
        if chosen:
            d = np.min(np.linalg.norm(Xn[:, None, :] - Xn[chosen][None, :, :], axis=2), axis=1)
            s = s * (1.0 - np.exp(-diversity_weight * d))   # penalise near-duplicates
        s[chosen] = -np.inf
        chosen.append(int(np.argmax(s)))

    batch = df.iloc[chosen].copy().reset_index(drop=True)
    batch["trial_rank"] = range(1, len(batch) + 1)
    batch["acquisition"] = "uncertainty x feasibility, greedy with diversity penalty [BO]"

    # [PC] joint batch risk -- how much of the batch dies if one shared assumption is wrong
    shared = {}
    for c in cols:
        v = batch[c].nunique()
        shared[c] = {"distinct_values": int(v), "all_same": bool(v == 1)}
    n_same = sum(1 for c in shared if shared[c]["all_same"])
    meta = {
        "k": len(batch),
        "shared_design_values": shared,
        "joint_batch_risk": (
            f"{n_same} of {len(cols)} design variables take a single value across the whole "
            f"batch. If that value rests on a wrong assumption, that fraction of the batch "
            f"is wasted together, not independently."
        ),
        "outside_support": (int((batch.get("inside_training_range") == False).sum())
                            if "inside_training_range" in batch else None),
    }
    return batch, meta


N_DESIGNS = 5        # [PC] designs handed back per order
N_EXPLORE = 3        # [PC] optional exploration proposals per order
N_CUBES = 6          # [IS] IS 516 (Part 1/Sec 1) cl 3.3 + 3.4: 3 cubes at 7 d + 3 at 28 d


def pick_designs(ranked, n=N_DESIGNS):
    """Pareto-front mixes first (cost vs carbon), then the cheapest of the rest. The models
    see total SCM, not the fly ash / GGBS split, so one per (binder, SCM, dose)."""
    if ranked is None or ranked.empty:
        return pd.DataFrame()
    r = ranked.copy()
    r["on_pareto_front"] = r.index.isin(set(pareto_front(r).index))
    d = (r.sort_values(["on_pareto_front", "cost_inr_m3"], ascending=[False, True])
          .drop_duplicates(["binder_kg_m3", "scm_frac", "sp_pct_binder"])
          .head(n).reset_index(drop=True))
    d.insert(0, "design_rank", range(1, len(d) + 1))
    d["validation_level"] = L0.ValidationLevel.COMPUTATIONALLY_COMPLIANT.name
    return d


def lab_package(req, state, *, wmodel, smodel, support, order_id,
                p_strength_min=0.90, p_slump_min=0.80, n_designs=N_DESIGNS,
                n_explore=N_EXPLORE, n_cubes=N_CUBES, sand_moisture_pct=None,
                ca_moisture_pct=None):
    """Everything a lab needs for one order. Never claims a result.

    Returns dict: status, designs, trials, batches, explore, notes.
    """
    notes = []
    serve_c, serve_meta = SC.screen(req, state, wmodel=wmodel, smodel=smodel,
                                    support=support, mode="serve")
    expl_c, _ = SC.screen(req, state, wmodel=wmodel, smodel=smodel,
                          support=support, mode="explore")
    ranked, rmeta = pd.DataFrame(), {}
    if len(serve_c):
        try:
            ranked, rmeta = rank_serve(serve_c, p_strength_min=p_strength_min,
                                       p_slump_min=p_slump_min, front_only=False)
        except ValueError as e:
            notes.append(f"REFUSED TO RANK: {e}")
    designs = pick_designs(ranked, n_designs)
    if len(designs):
        designs = designs.assign(order_id=order_id)

    # ---- the anchor for the IS 10262 cl 5.8 trial set -------------------------
    if len(designs):
        anchor, basis = designs.iloc[0], "design 1 (meets both thresholds)"
        status = "RANKED"
    elif len(serve_c) and serve_c["P_strength"].notna().any():
        anchor = serve_c.sort_values("P_strength", ascending=False).iloc[0]
        basis = (f"NO design met P_strength >= {p_strength_min} and P_slump >= {p_slump_min}. "
                 f"The trials bracket the in-support candidate with the highest P_strength "
                 f"({anchor['P_strength']:.2f}) to measure this plant's strength-vs-w/c line "
                 f"(IS 10262 cl 5.1, 5.8) -- they are learning trials, not a supply mix")
        status = "NO FEASIBLE DESIGN -- learning trials only"
    else:
        anchor, basis = None, "no in-support candidate: no trial set"
        status = "NO SERVE CANDIDATE"
    notes.append(f"trial anchor: {basis}")

    trials, batches = pd.DataFrame(), pd.DataFrame()
    if anchor is not None:
        wfit = wmodel["water_reduction_fit"]
        req_c = _replace(req, water_reduction_pct=float(
            WR.water_reduction_pct(float(anchor["dv_sp_pct_binder"]), wfit)))
        ts = L0.trial_set(req_c, state, binder_kg_m3=float(anchor["dv_binder_kg_m3"]),
                          flyash_frac=float(anchor["dv_flyash_frac"]),
                          ggbs_frac=float(anchor["dv_ggbs_frac"]),
                          admixture_pct_of_binder=float(anchor["dv_sp_pct_binder"]))
        ok = [t for t in ts if t["mix"] is not None]
        scored, _ = SC.screen(req, state, wmodel=wmodel, smodel=smodel, support=support,
                              mode="score", mixes=[t["mix"] for t in ok])
        if len(scored) != len(ok):
            raise RuntimeError("a trial mix was refused by the gate after trial_set built it")
        trials = scored.assign(
            order_id=order_id,
            trial_no=[t["trial_no"] for t in ok],
            trial_role=[t["role"] for t in ok],
            wcm_target=[t["wcm_target"] for t in ok],
            trial_note=[t["note"] for t in ok],
            anchor_basis=basis)
        for t in ts:
            if t["mix"] is None:
                notes.append(f"trial {t['trial_no']}: {t['note']}")
        vol = IS.trial_batch_volume(n_cubes, msa_mm=state.msa_mm)
        sm = sand_moisture_pct if sand_moisture_pct is not None else 0.0
        cm = ca_moisture_pct if ca_moisture_pct is not None else 0.0
        rows = []
        for t in ok:
            bs = L0.batch_sheet(t["mix"], state, volume_m3=vol["batch_m3"],
                                sand_moisture_pct=sm, ca_moisture_pct=cm)
            for r in bs["rows"]:
                rows.append({"order_id": order_id, "trial_no": t["trial_no"], **r,
                             "batch_m3": vol["batch_m3"],
                             "sand_moisture_pct_used": sm, "ca_moisture_pct_used": cm,
                             "sand_absorption_pct": state.sand_absorption_pct,
                             "ca_absorption_pct": state.ca_absorption_pct})
        batches = pd.DataFrame(rows)
        notes.append(f"batch volume {vol['batch_m3']:.3f} m3 = {n_cubes} cubes + slump + density "
                     f"+ {vol['waste_frac_pc']:.0%} margin [PC]; IS 1199 Pt 1 strength sample "
                     f">= 0.02 m3")

    explore, bmeta = pd.DataFrame(), {}
    # an exploration proposal must teach something NEW: drop the designs already handed
    # back and the trial anchor
    key = ["dv_binder_kg_m3", "dv_flyash_frac", "dv_ggbs_frac", "dv_sp_pct_binder"]
    seen = pd.concat([d[key] for d in (designs, pd.DataFrame([anchor]) if anchor is not None
                                       else pd.DataFrame()) if len(d)], ignore_index=True) \
        if (len(designs) or anchor is not None) else pd.DataFrame(columns=key)
    if len(expl_c) and len(seen):
        k_e = expl_c[key].round(6).astype(str).agg("|".join, axis=1)
        k_s = set(seen[key].round(6).astype(str).agg("|".join, axis=1))
        expl_c = expl_c[~k_e.isin(k_s)].reset_index(drop=True)
    if len(expl_c):
        explore, bmeta = propose_batch(expl_c, k=n_explore)
        explore = explore.assign(order_id=order_id,
                                 note="optional exploration proposal -- expert review before casting")
    return {"status": status, "designs": designs, "trials": trials, "batches": batches,
            "explore": explore, "explore_meta": bmeta, "notes": notes,
            "serve_meta": serve_meta, "rank_meta": rmeta,
            "best_P_strength": (float(serve_c["P_strength"].max()) if len(serve_c) else float("nan")),
            "n_serve": len(serve_c), "n_explore_candidates": len(expl_c)}
