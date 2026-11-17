"""Strength - IS 10262 Fig 1 baseline plus a residual GP.

GENERATED FILE - do not edit. Edit 10b_strength_residual_GP.ipynb and re-run its export cell.

Fig 1 is digitised from the three points IS 10262 PRINTS on the OPC 43 curve in
Annexes A-5/B-5/C-5, E-5 and F-5. The Abrams functional form is an engineering
choice; the anchors are Tier 1. Curves 1 and 3 have no printed anchors and are
refused rather than approximated.

w/c enters only through fig1_strength(), so its direction cannot be learned wrong.
predict_strength_mpa distinguishes mix mean / sample of three / one specimen.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import is_rules as IS

# [V] IS 10262:2019 Fig 1, OPC 43 grade curve. Each pair is PRINTED in the annex named.
#     These are read off the standard's own worked examples, not off the graph by eye.
IS10262_FIG1_OPC43_ANCHORS = (
    (0.61, 20.77, "Annex F-5"),
    (0.43, 38.25, "Annex E-5"),
    (0.36, 48.25, "Annex A-5 / B-5 / C-5"),
)

# [IS] Annex A-5: "(For PPC, the strength corresponding to OPC 43 grade curve is assumed
#      for the trial)." So PPC routes to this curve by the standard's own direction.
FIG1_CURVE_FOR = {
    "OPC43": "opc43", "PPC": "opc43", "PSC": "opc43",
    # [NV] Curves 1 and 3 have NO printed anchor points anywhere in IS 10262.
    "OPC33": None, "OPC53": None,
}


def _fit_fig1(anchors=IS10262_FIG1_OPC43_ANCHORS):
    """[EI] Abrams form through the printed anchors. Form is a choice; points are not."""
    wc = np.array([a[0] for a in anchors], dtype=float)
    fc = np.array([a[1] for a in anchors], dtype=float)
    b, a = np.polyfit(wc, np.log(fc), 1)
    return float(a), float(b)


FIG1_A, FIG1_B = _fit_fig1()


class CurveNotDigitised(LookupError):
    """Raised for a cement class whose Fig 1 curve has no printed anchor points."""


def fig1_strength(wc_ratio, cement_type="PPC"):
    """[V]/[EI] 28-day strength Fig 1 implies for a free water-cement ratio.

    Refuses for OPC 33 and OPC 53: IS 10262 prints no anchor point on Curves 1 or 3,
    so a value for them would be invented. NOT VERIFIED FROM PRIMARY STANDARD SOURCE.
    """
    curve = FIG1_CURVE_FOR.get(str(cement_type).upper().replace(" ", ""))
    if curve is None:
        raise CurveNotDigitised(
            f"IS 10262 Fig 1 has three curves selected by expected 28-day cement "
            f"strength, but prints anchor points only on the OPC 43 grade curve. "
            f"Cement type {cement_type!r} needs Curve 1 or Curve 3, which is "
            f"NOT VERIFIED FROM PRIMARY STANDARD SOURCE. Read the printed figure, or "
            f"flag the mix as using a Curve 2 approximation and record that decision."
        )
    return np.exp(FIG1_A + FIG1_B * np.asarray(wc_ratio, dtype=float))


def fig1_wc_for_strength(target_mean_mpa, cement_type="PPC"):
    """[V]/[EI] The inverse -- the direction Fig 1 is actually READ in (cl 5.2)."""
    curve = FIG1_CURVE_FOR.get(str(cement_type).upper().replace(" ", ""))
    if curve is None:
        raise CurveNotDigitised(f"no digitised Fig 1 curve for {cement_type!r}")
    return (np.log(np.asarray(target_mean_mpa, dtype=float)) - FIG1_A) / FIG1_B


# [PC] Anything that is a function of the water-cement ratio. The residual may not see
#      these, or it can re-learn -- and re-break -- the direction Fig 1 fixes.
WC_DERIVED = frozenset({
    "wb_ratio", "wc_ratio", "wc_counted", "water_kg_m3", "water_batched",
    "free_water", "paste_frac",
})

# [ML] What the residual IS allowed to see. cement_28d_strength is the material fact
#      Fig 1's curve selection depends on and which a single curve cannot carry.
STRENGTH_RESIDUAL_FEATURES = [
    "cement_28d_strength",
    "binder_kg_m3",
    "scm_frac",
    "sp_pct_binder",
    "agg_binder_ratio",
    "fine_frac_of_agg",
    "msand_frac",
]


def check_no_wc_leak(features):
    """Gate G10, enforced at build time rather than hoped for at test time."""
    leak = sorted(set(features) & WC_DERIVED)
    if leak:
        raise ValueError(
            f"features {leak} are functions of the water-cement ratio. w/c may enter the "
            f"strength prediction only through fig1_strength(), or gate G10 is void."
        )
    return True


check_no_wc_leak(STRENGTH_RESIDUAL_FEATURES)


from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler


def fit_strength_model(df, features=None, *, fc_col="fc_mpa", wc_col="wb_ratio",
                       cement_type="PPC", seed=0):
    """Fit the residual GP on measured minus Fig 1. Returns the dict screen.py expects."""
    features = list(features or STRENGTH_RESIDUAL_FEATURES)
    features = [f for f in features if f in df.columns]
    check_no_wc_leak(features)

    sub = df.dropna(subset=features + [fc_col, wc_col]).copy()
    base = fig1_strength(sub[wc_col], cement_type=cement_type)
    y = (sub[fc_col].to_numpy(float) - np.asarray(base, dtype=float))

    scaler = StandardScaler().fit(sub[features].to_numpy(float))
    X = scaler.transform(sub[features].to_numpy(float))

    # [ML] Length scales are bounded AWAY FROM ZERO and the noise away from zero too.
    #      Left free, the optimiser drives a length scale to ~0.02 on a standardised
    #      feature and the GP interpolates the 256 samples exactly -- in-sample MAE
    #      0.000 N/mm2 and a predictive sd of 0.003. Concrete does not behave that way:
    #      [IS] IS 456 Table 8 assumes a standard deviation of 4.0 N/mm2 for M25-M50 even
    #      under good control. A model that admits no scatter would turn P_strength into
    #      a 0/1 step, which is the failure this pipeline already fixed once.
    kern = (ConstantKernel(1.0, (1e-3, 1e4))
            * RBF(length_scale=np.ones(X.shape[1]), length_scale_bounds=(2e-1, 1e3))
            + WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-2, 1e4)))
    gp = GaussianProcessRegressor(kernel=kern, normalize_y=True,
                                  n_restarts_optimizer=5, random_state=seed)
    gp.fit(X, y)

    # The WhiteKernel noise_level lives in the NORMALISED y space while
    # predict(return_std=True) returns a standard deviation in ORIGINAL units.
    # Rescale once, here, and record that it is already rescaled -- screen.py keys off
    # this flag and an earlier version rescaled it a second time.
    y_std = float(getattr(gp, "_y_train_std", 1.0))
    noise = float(gp.kernel_.k2.noise_level) * (y_std ** 2)

    return {"gp": gp, "scaler": scaler, "features": features,
            "noise_var": noise, "noise_in_normalised_units": False,
            "y_train_std": y_std, "n": len(sub),
            "cement_type": cement_type, "wc_col": wc_col,
            "kernel": str(gp.kernel_),
            "feature_median": {f: float(np.nanmedian(sub[f].to_numpy(float))) for f in features},
            "wc_range": (float(sub[wc_col].min()), float(sub[wc_col].max())),
            "fig1": {"a": FIG1_A, "b": FIG1_B, "anchors": IS10262_FIG1_OPC43_ANCHORS},
            "trained_on_groups": sorted(map(str, sub.get("design_grp", pd.Series(dtype=str)).unique()))}


def predict_strength_mpa(model, df, kind="mean", floor_sd_mpa=None):
    """Predicted 28-day strength. THREE different questions, three answers.

    kind='mean'     -> the mean strength of the MIX. The WhiteKernel measurement-noise
                       term is REMOVED: it describes scatter of samples about that mean.
    kind='sample'   -> the mean of THREE specimens, [IS] IS 456 cl 15.3. This is what
                       fc_mpa records and what acceptance is judged on, so it is what
                       P_strength should use.
    kind='specimen' -> ONE cube. Widest. [IS] cl 15.4 allows +/-15 percent within a sample.

    Collapsing these is how the previous optimiser inflated every interval.
    """
    if kind not in ("mean", "sample", "specimen"):
        raise ValueError("kind must be 'mean', 'sample' or 'specimen'")
    X = model["scaler"].transform(df[model["features"]].to_numpy(float))
    mu_res, sd_full = model["gp"].predict(X, return_std=True)
    var_mean = np.maximum(sd_full ** 2 - model["noise_var"], 1e-12)

    if kind == "mean":
        var = var_mean
    elif kind == "sample":
        # the sample is already a mean of three, and fc_mpa was fitted as such, so the
        # fitted noise IS the sample-level noise
        var = var_mean + model["noise_var"]
    else:
        # [PC] one specimen. IS 456 cl 15.3 makes a sample the mean of three, so a single
        #      specimen's variance about the mix mean is about three times the sample's.
        var = var_mean + 3.0 * model["noise_var"]

    base = fig1_strength(df[model["wc_col"]], cement_type=model["cement_type"])
    sd = np.sqrt(var)

    # [PC] The GP's sd is an IN-SAMPLE quantity. For a mix the model has not seen, it
    #      cannot be more certain than it was about a held-out family, so the sd is
    #      floored at the leave-one-family-out RMSE. Without this floor a near-
    #      interpolating fit reports ~0 and P_strength becomes a step function.
    floor = floor_sd_mpa if floor_sd_mpa is not None else model.get("out_of_family_rmse_mpa")
    if floor is not None:
        sd = np.maximum(sd, float(floor))
    return np.asarray(base) + mu_res, sd


def p_meets_target(model, df, target_mean_mpa, kind="sample", floor_sd_mpa=None):
    """P(strength >= target mean strength). [IS] cl 4.2 sets the target; this is the
    probability a SAMPLE (cl 15.3, mean of three) reaches it."""
    from scipy.stats import norm
    mu, sd = predict_strength_mpa(model, df, kind=kind, floor_sd_mpa=floor_sd_mpa)
    return 1.0 - norm.cdf((np.asarray(target_mean_mpa, dtype=float) - mu) / np.maximum(sd, 1e-9))
