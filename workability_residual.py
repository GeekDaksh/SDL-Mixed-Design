"""Workability - IS 10262 baseline plus a residual GP.

GENERATED FILE - do not edit. Edit 10_workability_residual_GP.ipynb and re-run its export cell.

Water enters the slump prediction ONLY through is_slump_baseline(), whose slope
is fixed by IS 10262:2019 Table 4 + cl 5.3. The GP never sees a water-derived
feature, so the water direction cannot be learned wrong (gate G1).

predict_slump(kind='mean') REMOVES the WhiteKernel term; kind='specimen' keeps it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import is_rules as IS

def is_design_family(key) -> bool:
    """[PC] A real design family has a design ID, not a numeric concatenation.

    Keys like '150.0|110.0|0.0|170.' are rows whose design identity was lost
    upstream; keys like 'M30-P-20MS-01' are design families. The test is whether
    the key contains a letter.
    """
    return isinstance(key, str) and any(ch.isalpha() for ch in key)


def split_quarantine(df, group_col="design_grp", min_rows=3):
    """Separate real design families from orphans. Returns (kept, quarantined, report)."""
    counts = df[group_col].value_counts()
    keep_keys = [k for k, n in counts.items() if is_design_family(k) and n >= min_rows]
    kept = df[df[group_col].isin(keep_keys)].copy()
    quar = df[~df[group_col].isin(keep_keys)].copy()
    report = {
        "n_rows_in": len(df),
        "n_rows_kept": len(kept),
        "n_rows_quarantined": len(quar),
        "groups_in": int(df[group_col].nunique()),
        "groups_kept": len(keep_keys),
        "kept_keys": sorted(keep_keys),
        "quarantined_keys": sorted(map(str, quar[group_col].unique())),
        "rule": f"[PC] keep groups with an alphabetic design ID and at least {min_rows} rows",
    }
    return kept, quar, report


def _table4_base(msa_mm, ca_shape="angular"):
    # [IS] Table 4 row + cl 5.3 shape adjustment, elementwise. Refuses unlisted rows.
    adj = IS.IS10262_CL_5_3_SHAPE_ADJUST_KG[ca_shape]
    rows = IS.IS10262_TABLE4_WATER

    def one(m):
        m = float(m)
        key = m if m in rows else (int(m) if int(m) == m and int(m) in rows else None)
        if key is None:
            raise IS.MissingTableRow(
                f"IS 10262 Table 4 prints no row for msa {m} mm. "
                f"Printed rows: {sorted(rows)}. Do not interpolate."
            )
        return rows[key] + adj

    arr = np.asarray(msa_mm)
    if arr.ndim == 0:
        return float(one(arr.item()))
    return np.array([one(v) for v in arr.ravel()], dtype=float).reshape(arr.shape)


def is_slump_baseline(water_kg_m3, msa_mm, ca_shape="angular",
                      water_reduction_pct=0.0):
    """[EI] The IS-implied slump for a batch. Mean function for the GP.

    IS 10262 cl 5.3 has TWO separate provisions and they must not be collapsed:

      (a) water demand rises with target slump -- about 3 percent per 25 mm, on the
          Table 4 base. This is the slump-water relation.
      (b) the water so calculated MAY THEN BE REDUCED by chemical admixture, 5-10
          percent for water reducers and 20-30 percent and above for superplasticizers.

    Provision (b) is taken *in order to hold the same slump*. Annex A-6 computes 191.58
    kg for 75 mm and then batches far less because a superplasticizer is used -- the
    mix is still a 75 mm mix. So the slump a batch implies is the slump that generated
    its GROSS water, not the slump you would read off its net water.

    Inverting the net water directly -- which an earlier version of this notebook did --
    says that adding superplasticizer LOWERS slump, because it lowers water. That is
    backwards, and it was visible in the screen: predicted slump fell from 103 to 34 mm
    as the dose rose.

    So the net water is un-reduced first:

        W_gross = W_net / (1 - reduction/100)
        S       = 50 + (W_gross / W_table4 - 1) x (25 / 0.03)

    `water_reduction_pct` must come from a source independent of the measured slump --
    `water_reduction_pct(sp_dose, fit)` from the dose -- or the baseline is circular.

    Still NOT a predicted slump: it carries no plant effect, no aggregate shape beyond
    the cl 5.3 offset, no temperature. The residual model supplies those.
    """
    base = _table4_base(msa_mm, ca_shape)
    pct = IS.IS10262_CL_5_3_SLUMP_PCT_PER_25MM / 100.0
    w_net = np.asarray(water_kg_m3, dtype=float)
    red = np.asarray(water_reduction_pct, dtype=float) / 100.0
    if np.any(red >= 1.0):
        raise ValueError("water reduction of 100 percent or more is not physical")
    w_gross = w_net / (1.0 - red)
    return 50.0 + (w_gross / base - 1.0) * (25.0 / pct)


def is_slump_slope(msa_mm, ca_shape="angular"):
    """[EI] dS/dW in mm of slump per kg of water. Constant for a given msa."""
    base = _table4_base(msa_mm, ca_shape)
    return (25.0 / (IS.IS10262_CL_5_3_SLUMP_PCT_PER_25MM / 100.0)) / base


# [PC] Anything that is a function of batch water. The residual model may not see these,
#      or it can re-learn -- and re-break -- the direction the baseline exists to fix.
WATER_DERIVED = frozenset({
    "water_kg_m3", "water_batched", "free_water", "wb_ratio", "wc_ratio", "paste_frac",
})

# [PC] What the residual IS allowed to see. SP dose is mandatory: it is the thing water
#      is confounded with, and the strongest legitimate correlate of slump in this data.
RESIDUAL_FEATURES = [
    "sp_pct_binder",        # [IS] IS 9103 cl 10.2 bounds it; the model learns inside that
    "binder_kg_m3",
    "scm_frac",
    "fine_frac_of_agg",     # determined by IS 10262 Table 5 in Layer 0, but it VARIES by zone
    "msand_frac",
    "agg_binder_ratio",
    "concrete_temp",        # [IS] cl 5.3 names temperature as a water-demand driver
]


def check_no_water_leak(features):
    """Gate G1, enforced at build time rather than hoped for at test time."""
    leak = sorted(set(features) & WATER_DERIVED)
    if leak:
        raise ValueError(
            f"features {leak} are functions of batch water. Water may enter the slump "
            f"prediction only through is_slump_baseline(), or gate G1 is void."
        )
    return True


check_no_water_leak(RESIDUAL_FEATURES)


def implied_water_reduction_pct(water_kg_m3, slump_mm, msa_mm, ca_shape="angular"):
    """[V] The cl 5.3 reduction a batch actually used, backed out of the record.

        reduction = 1 - (water batched) / (Table 4 + cl 5.3 demand for the MEASURED slump)

    This is an OBSERVATION, not a standard value: cl 5.3 gives ranges and an explicit
    "or may be established by trial". This is that trial, run on the plant's own history.
    """
    demand = np.array([
        IS.water_content("M30", float(m), float(s), ca_shape=ca_shape)["water_kg_m3"]
        for m, s in zip(np.atleast_1d(msa_mm), np.atleast_1d(slump_mm))])
    return 100.0 * (1.0 - np.atleast_1d(np.asarray(water_kg_m3, float)) / demand)


def fit_water_reduction(df, *, water_col="water_kg_m3", slump_col="slump_mm",
                        msa_col="msa", sp_col="sp_pct_binder"):
    """[V] Fit reduction% against superplasticiser dose. Straight line, no tuning.

    Returns the coefficients plus a leave-one-family-out error, so the number that
    goes into Layer 0 carries its own out-of-family accuracy.
    """
    d = df.dropna(subset=[water_col, slump_col, msa_col, sp_col]).copy()
    y = implied_water_reduction_pct(d[water_col], d[slump_col], d[msa_col])
    x = d[sp_col].to_numpy(float)
    b, a = np.polyfit(x, y, 1)
    pred = a + b * x
    r2 = 1.0 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2)

    errs, per_family = [], []
    if "design_grp" in d:
        for g in sorted(d["design_grp"].unique()):
            tr, te = d[d["design_grp"] != g], d[d["design_grp"] == g]
            if len(tr) < 5 or len(te) < 2:
                continue
            ytr = implied_water_reduction_pct(tr[water_col], tr[slump_col], tr[msa_col])
            bb, aa = np.polyfit(tr[sp_col].to_numpy(float), ytr, 1)
            yte = implied_water_reduction_pct(te[water_col], te[slump_col], te[msa_col])
            e = (aa + bb * te[sp_col].to_numpy(float)) - yte
            errs.extend(e.tolist())
            per_family.append({"group": g, "n": len(te), "bias_pp": float(np.mean(e)),
                               "mae_pp": float(np.mean(np.abs(e)))})

    return {"intercept_pct": float(a), "slope_pct_per_sp_pct": float(b),
            "r2": float(r2), "n": len(d),
            # the ranges this relation was FITTED on. Outside them it is extrapolation,
            # and it sets the water for every candidate -- so it must be guarded.
            "sp_pct_range": (float(d[sp_col].min()), float(d[sp_col].max())),
            "water_kg_m3_range": (float(d[water_col].min()), float(d[water_col].max())),
            "slump_mm_range": (float(d[slump_col].min()), float(d[slump_col].max())),
            "logo_mae_pp": float(np.mean(np.abs(errs))) if errs else None,
            "per_family": per_family,
            "basis": ("[V] fitted from this plant's own families; IS 10262 cl 5.3 permits "
                      "the reduction but states no value")}


def water_reduction_pct(sp_pct_of_binder, fit):
    """[V] The cl 5.3 reduction to hand Layer 0 for a given admixture dose."""
    return fit["intercept_pct"] + fit["slope_pct_per_sp_pct"] * np.asarray(
        sp_pct_of_binder, dtype=float)


def inside_fitted_range(fit, *, sp_pct=None, water_kg_m3=None, slump_mm=None):
    """[PC] Is a candidate inside the range the cl 5.3 relation was fitted on?

    The support box in notebook 11 covers the GP's seven features. Water is
    deliberately NOT one of them -- that is what makes gate G1 hold by construction --
    so nothing there guards water. But the reduction relation and the baseline were
    both fitted inside a narrow water band, and the relation now SETS the water for
    every candidate. Outside that band both are extrapolating, unguarded.

    Returns a per-axis verdict. True means inside; None means not checked.
    """
    out = {}
    for name, val, key in (("sp_pct_binder", sp_pct, "sp_pct_range"),
                           ("water_kg_m3", water_kg_m3, "water_kg_m3_range"),
                           ("slump_mm", slump_mm, "slump_mm_range")):
        if val is None or key not in fit:
            out[name] = None
            continue
        lo, hi = fit[key]
        v = np.asarray(val, dtype=float)
        out[name] = (v >= lo) & (v <= hi)
        out[name + "_range"] = (lo, hi)
    return out


from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler


def build_gp(seed=0):
    """[ML] Residual GP. WhiteKernel is the MEASUREMENT noise term -- see predict()."""
    k = (ConstantKernel(1.0, (1e-3, 1e4))
         * RBF(length_scale=np.ones(1), length_scale_bounds=(1e-2, 1e3))
         + WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-6, 1e4)))
    return GaussianProcessRegressor(kernel=k, normalize_y=True,
                                    n_restarts_optimizer=5, random_state=seed)


def fit_residual_model(df, features=None, *, slump_col="slump_mm",
                       water_col="water_kg_m3", msa_col="msa", seed=0,
                       water_fit=None, sp_col="sp_pct_binder"):
    """Fit the residual GP. Returns a dict carrying everything predict() needs.

    water_fit is the cl 5.3 reduction relation from fit_water_reduction(). It is
    REQUIRED: without it the baseline inverts net water and the admixture dose comes
    out with the wrong sign on slump.
    """
    if water_fit is None:
        raise ValueError(
            "fit_residual_model needs water_fit from fit_water_reduction(). Without the "
            "cl 5.3 reduction the baseline treats a water saving as a slump loss, which "
            "inverts the admixture effect.")
    features = list(features or RESIDUAL_FEATURES)
    features = [f for f in features if f in df.columns]
    check_no_water_leak(features)

    sub = df.dropna(subset=features + [slump_col, water_col, msa_col, sp_col]).copy()
    red = water_reduction_pct(sub[sp_col].to_numpy(float), water_fit)
    base = is_slump_baseline(sub[water_col], sub[msa_col], water_reduction_pct=red)
    y = (sub[slump_col] - base).to_numpy(float)

    scaler = StandardScaler().fit(sub[features].to_numpy(float))
    X = scaler.transform(sub[features].to_numpy(float))

    kern = (ConstantKernel(1.0, (1e-3, 1e4))
            * RBF(length_scale=np.ones(X.shape[1]), length_scale_bounds=(1e-2, 1e3))
            + WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-6, 1e4)))
    gp = GaussianProcessRegressor(kernel=kern, normalize_y=True,
                                  n_restarts_optimizer=5, random_state=seed)
    gp.fit(X, y)

    # The WhiteKernel noise_level lives in the NORMALISED y space, while
    # gp.predict(return_std=True) returns a standard deviation in ORIGINAL units.
    # Comparing them directly is a units error -- exactly the class of mistake the old
    # optimiser made -- so rescale it here, once, and store it in original units.
    y_std = float(getattr(gp, "_y_train_std", 1.0))
    noise = float(gp.kernel_.k2.noise_level) * (y_std ** 2)
    return {"gp": gp, "scaler": scaler, "features": features, "noise_var": noise,
            "water_fit": water_fit, "sp_col": sp_col,
            "noise_in_normalised_units": False,     # already rescaled above -- do not rescale again
            "y_train_std": y_std,
            "feature_median": {f: float(np.nanmedian(sub[f].to_numpy(float))) for f in features},
            "n": len(sub), "kernel": str(gp.kernel_),
            "trained_on_groups": sorted(map(str, sub.get("design_grp", pd.Series(dtype=str)).unique()))}


def predict_slump(model, df, *, water_col="water_kg_m3", msa_col="msa", kind="mean"):
    """Predicted slump = IS baseline + residual GP.

    kind='mean'     -> uncertainty of the MEAN slump of a mix. The WhiteKernel
                       measurement-noise term is REMOVED, because it describes the
                       scatter of individual readings about that mean.
    kind='specimen' -> uncertainty of ONE slump reading. The noise term is kept.

    These are different questions and IS 456 treats them differently (cl 15.1.1 and
    cl 16.1 for strength). Adding the noise term on top of a GP sd that already
    contains it -- as the previous optimiser did -- inflates every interval and
    makes the feasibility test reject good mixes.
    """
    if kind not in ("mean", "specimen"):
        raise ValueError("kind must be 'mean' or 'specimen'")
    X = model["scaler"].transform(df[model["features"]].to_numpy(float))
    mu_res, sd_full = model["gp"].predict(X, return_std=True)
    var = np.maximum(sd_full ** 2, 0.0)
    if kind == "mean":
        var = np.maximum(var - model["noise_var"], 1e-12)   # REMOVE, never add
    red = water_reduction_pct(df[model.get("sp_col", "sp_pct_binder")].to_numpy(float),
                              model["water_fit"])
    base = is_slump_baseline(df[water_col], df[msa_col], water_reduction_pct=red)
    return np.asarray(base) + mu_res, np.sqrt(var)


def logo_error(residuals_mm, per_group_bias_mm):
    """[PC] Out-of-group error, split into the two parts that behave differently.

    The GP's own sd is an IN-SAMPLE quantity -- about 2.7 mm here, against a
    leave-one-group-out error that reaches 40 mm. Using the in-sample sd would make
    the system announce a band it cannot hold.

    But the out-of-group error is NOT scatter. Most of it is a per-family systematic
    OFFSET: for two of five families |bias| equals MAE exactly, meaning every held-out
    row errs the same way. Treating an offset as the sigma of a symmetric normal
    centred on mu understates how wrong a single family can be -- measured coverage of
    the nominal 90 percent band was 43 percent for one family.

    So both are returned and both must be used: `rmse_mm` for the width, `bias_rms_mm`
    for how far the centre itself can sit from the truth.
    """
    r = np.asarray(residuals_mm, dtype=float)
    b = np.asarray(per_group_bias_mm, dtype=float)
    return {
        "rmse_mm": float(np.sqrt(np.mean(r ** 2))),
        "sd_mm": float(np.std(r, ddof=1)),
        "bias_rms_mm": float(np.sqrt(np.mean(b ** 2))),
        "bias_max_mm": float(np.max(np.abs(b))),
        "note": ("rmse_mm is the width; bias_rms_mm is how far the CENTRE can sit from "
                 "the truth for an unseen family. Quote both, never rmse alone."),
    }


def pooled_skill(logo_df):
    """[PC] Pooled 1 - SUM(SS_res)/SUM(SS_base), not the mean of per-group ratios.

    With group sums of squares spanning 7682 to 11767, the mean of five ratios is
    dominated by the single worst fold and is not the quantity anyone means by skill.
    """
    return float(1.0 - logo_df["ss_res"].sum() / logo_df["ss_base"].sum())


def achievable(model, df, target_slump_mm, tolerance_mm=25.0, confidence=0.90,
               *, out_of_group_sd_mm, out_of_group_bias_mm=0.0,
               water_col="water_kg_m3", msa_col="msa"):
    """[PC] Can this slump band be held, at this confidence, for a NEW mix?

    out_of_group_sd_mm is REQUIRED and has no default. It is the honest error scale,
    measured by leave-one-group-out in this notebook. The check uses the LARGER of it
    and the GP's own sd, because a model cannot be more certain about a new mix than
    it was about a held-out family.

    tolerance_mm default 25 mm: [IS] IS 456 cl 7.1 and IS 4926 give the acceptance
    bands for workability, and is_rules.slump_acceptance_band is the authority once a
    specified value is in hand. 25 mm is only this caller's default.

    Returns a verdict a person can read, not just a boolean.
    """
    from scipy.stats import norm
    mu, sd_in = predict_slump(model, df, kind="mean")
    sd = np.maximum(sd_in, float(out_of_group_sd_mm))
    z = norm.ppf(0.5 + confidence / 2.0)
    half_width = z * sd

    # Two separate ways to miss, and they need separate verdicts:
    #   OFFSET  -- the predicted mean is already outside the band
    #   WIDTH   -- the band is narrower than the model's own uncertainty
    # The earlier version tested only WIDTH, so a mix predicted 156 mm off target was
    # reported as a 38 mm uncertainty problem. Bias is not variance.
    mu = np.atleast_1d(mu)
    offset = np.abs(mu - float(target_slump_mm))
    offset_ok = offset <= tolerance_mm
    # an unseen family's centre can itself sit this far out
    offset_ok_after_bias = (offset + float(out_of_group_bias_mm)) <= tolerance_mm
    width_ok = np.atleast_1d(half_width) <= tolerance_mm
    can = offset_ok_after_bias & width_ok

    verdict = []
    for o, ook, obk, w, h in zip(offset, offset_ok, offset_ok_after_bias,
                                 width_ok, np.atleast_1d(half_width)):
        if not ook:
            verdict.append(
                f"NOT achievable -- OFFSET: the predicted mean is {o:.0f} mm from the "
                f"{target_slump_mm:.0f} mm target, outside the +/-{tolerance_mm:.0f} mm band "
                f"before uncertainty is even considered. This is bias, not variance.")
        elif not obk:
            verdict.append(
                f"NOT achievable -- OFFSET plus family drift: predicted mean is {o:.0f} mm "
                f"out, and an unseen family's centre moves a further "
                f"{out_of_group_bias_mm:.0f} mm on this data.")
        elif not w:
            verdict.append(
                f"NOT achievable -- WIDTH: the mean is on target but a +/-{tolerance_mm:.0f} mm "
                f"band cannot be guaranteed at {confidence:.0%}; the honest half-width is "
                f"{h:.0f} mm.")
        else:
            verdict.append("achievable")

    return {
        "target_slump_mm": target_slump_mm,
        "tolerance_mm": tolerance_mm,
        "confidence": confidence,
        "predicted_mean_mm": mu,
        "offset_from_target_mm": offset,
        "model_sd_in_sample_mm": sd_in,
        "out_of_group_sd_mm": float(out_of_group_sd_mm),
        "out_of_group_bias_mm": float(out_of_group_bias_mm),
        "sd_used_mm": sd,
        "required_half_width_mm": half_width,
        "offset_ok": offset_ok,
        "width_ok": width_ok,
        "achievable": can,
        "verdict": verdict,
    }
