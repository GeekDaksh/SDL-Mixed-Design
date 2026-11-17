"""GENERATED FILE - do not edit. Edit 18_P1_PPC_ai_models_next_experiments.ipynb and re-run."""
# MODULE: exported to p1_ppc_loop.py
"""P1 on PPC -- helpers that let the SDL's own AI models (notebooks 10 / 10b) learn from
the lab's results, and that measure BEFORE casting how much a planned trial will teach.

[BO] Bayesian experimental design is a PROJECT RESEARCH METHOD, not an IS requirement.
[ML] The models are the notebook 10 slump GP and the notebook 10b strength GP. Nothing here
     changes their hyperparameters; new results are added as data (an exact Bayesian update
     with the fitted kernel), so a handful of lab rows cannot distort what 256 rows taught.
"""
import numpy as np
import pandas as pd
from scipy.linalg import solve_triangular, cho_solve
from sklearn.gaussian_process import GaussianProcessRegressor

import is_rules as IS
import workability_residual as WR
import strength_residual as SR

LOG_PATH = "P1_PPC_results_log.csv"
# outcome words the lab may write; only the MEASURED ones become training rows
# (same rule as loop.py: a rejection with no cast is not an observation)
MEASURED = ("measured", "measured_workability", "measured_strength")
NOT_MEASURED = ("human_rejected_before_cast", "material_unavailable", "cost_rejected",
                "constructability_rejected", "other_project_constraint", "experiment_failed")
LAB_COLS = ["outcome", "reviewer", "reason", "batch_id", "cast_date",
            "actual_free_water_kg_m3", "concrete_temp_15min_c",
            "slump_15min_mm", "slump_45min_mm", "slump_60min_mm", "slump_shape",
            "fc_7d_1", "fc_7d_2", "fc_7d_3", "fc_28d_1", "fc_28d_2", "fc_28d_3", "lab_notes"]


def scaled(model, df):
    return model["scaler"].transform(df[model["features"]].to_numpy(float))


def _parts(model):
    gp = model["gp"]
    k = gp.kernel_
    return gp, k.k1, float(k.k2.noise_level), float(np.atleast_1d(gp._y_train_std)[0])


def information(model, obs_df, use_df=None):
    """How much casting the rows of obs_df teaches the model (one reading per batch).

    bits      = mutual information between the planned readings and the model's unknown
                residual surface (0.5 log2 det(I + S/noise)).
    sd_before / sd_after = mean predictive sd (mm or MPa) of the model's correction over
                use_df, before and after those readings arrive.
    """
    gp, k_sig, sn, ys = _parts(model)
    Zo = scaled(model, obs_df)
    Z = Zo if use_df is None or len(use_df) == 0 else np.vstack([Zo, scaled(model, use_df)])
    v = solve_triangular(gp.L_, k_sig(gp.X_train_, Z), lower=True)
    S = k_sig(Z) - v.T @ v
    S = 0.5 * (S + S.T)
    n = len(Zo)
    Soo = S[:n, :n]
    _, ld = np.linalg.slogdet(np.eye(n) + Soo / sn)
    out = {"bits": float(0.5 * ld / np.log(2.0))}
    if Z.shape[0] > n:
        Suu, Suo = S[n:, n:], S[n:, :n]
        A = np.linalg.solve(Soo + sn * np.eye(n), Suo.T)
        before = np.clip(np.diag(Suu), 0, None)
        after = np.clip(before - np.sum(Suo * A.T, axis=1), 0, None)
        out["sd_before"] = float(np.mean(np.sqrt(before)) * ys)
        out["sd_after"] = float(np.mean(np.sqrt(after)) * ys)
    return out


def condition(model, X_df, y_resid, groups, tag):
    """Exact Bayesian update of a fitted GP with new rows. Hyperparameters and the
    original y-normalisation are kept, so the kernel keeps its meaning."""
    if len(X_df) == 0:
        return model
    gp = model["gp"]
    m0 = float(np.atleast_1d(gp._y_train_mean)[0])
    s0 = float(np.atleast_1d(gp._y_train_std)[0])
    y_old = np.asarray(gp.y_train_, float).ravel() * s0 + m0
    X = np.vstack([gp.X_train_, scaled(model, X_df)])
    y = np.concatenate([y_old, np.asarray(y_resid, float)])
    g2 = GaussianProcessRegressor(kernel=gp.kernel_, alpha=gp.alpha, optimizer=None,
                                  normalize_y=True)
    g2.fit(X, y)
    g2._y_train_mean, g2._y_train_std = m0, s0
    g2.y_train_ = (y - m0) / s0
    g2.alpha_ = cho_solve((g2.L_, True), g2.y_train_, check_finite=False)
    out = dict(model)
    out["gp"] = g2
    out["n"] = int(len(y))
    out["trained_on_groups"] = sorted(set(map(str, model.get("trained_on_groups", [])))
                                      | set(map(str, groups)))
    out["updated_with"] = list(model.get("updated_with", [])) + [tag]
    return out


def read_log(path=LOG_PATH):
    from pathlib import Path
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, dtype={"outcome": str, "batch_id": str})


def measured_rows(log):
    """Training rows from the lab log. One physical batch = one row (statistical integrity)."""
    if log is None or log.empty:
        return pd.DataFrame(), pd.DataFrame(), []
    d = log.copy()
    oc = d["outcome"].fillna("").astype(str).str.strip().str.lower()
    unknown = sorted(set(oc) - set(MEASURED) - set(NOT_MEASURED) - {""})
    d = d[oc.isin(MEASURED)].copy()
    notes = [f"unknown outcome words ignored: {unknown}"] if unknown else []
    if d.empty:
        return pd.DataFrame(), pd.DataFrame(), notes
    d["batch_key"] = d["batch_id"].where(d["batch_id"].notna() & (d["batch_id"].astype(str) != ""),
                                         d["trial_id"])
    num = lambda c: pd.to_numeric(d[c], errors="coerce")
    d["water_used"] = num("actual_free_water_kg_m3").fillna(num("water_kg_m3"))
    d["concrete_temp"] = num("concrete_temp_15min_c").fillna(num("concrete_temp"))
    w = d[num("slump_15min_mm").notna()].copy()
    w["slump_mm"] = pd.to_numeric(w["slump_15min_mm"], errors="coerce")
    w = w.drop_duplicates("batch_key", keep="last")
    s_rows = []
    for _, r in d.iterrows():
        cubes = [pd.to_numeric(r.get(f"fc_28d_{i}"), errors="coerce") for i in (1, 2, 3)]
        if any(pd.isna(c) for c in cubes):
            continue
        res = IS.sample_test_result([float(c) for c in cubes])
        if not res["valid"]:
            notes.append(f"{r['trial_id']}: 28-d cubes spread {res['max_deviation_pct']:.3f} % > 15 % "
                         f"-> sample invalid (IS 456 cl 15.4), not used")
            continue
        s_rows.append({**r.to_dict(), "fc_mpa": res["result_mpa"]})
    s = pd.DataFrame(s_rows)
    if len(s):
        s = s.drop_duplicates("batch_key", keep="last")
    return w, s, notes


def update_models(wmodel, smodel, log):
    """Add the lab's measured batches to both AI models. Returns (wmodel, smodel, report)."""
    w, s, notes = measured_rows(log)
    rep = {"n_slump_batches": int(len(w)), "n_strength_batches": int(len(s)), "notes": notes,
           "slump_errors": [], "strength_errors": []}
    if len(w):
        X = w.copy()
        X["water_kg_m3"] = X["water_used"]
        for f in wmodel["features"]:
            X[f] = pd.to_numeric(X[f], errors="coerce")
        X = X.dropna(subset=wmodel["features"] + ["water_kg_m3", "msa", "sp_pct_binder"])
        red = WR.water_reduction_pct(X["sp_pct_binder"].to_numpy(float), wmodel["water_fit"])
        base = WR.is_slump_baseline(X["water_kg_m3"], X["msa"].astype(float), water_reduction_pct=red)
        y = X["slump_mm"].to_numpy(float) - np.asarray(base, float)
        mu_before, _ = WR.predict_slump(wmodel, X, kind="mean")
        rep["slump_errors"] = [{"trial_id": t, "predicted_mm": float(p), "measured_mm": float(m)}
                               for t, p, m in zip(X["trial_id"], mu_before, X["slump_mm"])]
        wmodel = condition(wmodel, X, y, X["batch_key"], f"{len(X)} P1-PPC lab batches")
    if len(s) and smodel is not None:
        X = s.copy()
        for f in smodel["features"] + [smodel["wc_col"]]:
            X[f] = pd.to_numeric(X[f], errors="coerce")
        X = X.dropna(subset=smodel["features"] + [smodel["wc_col"]])
        base = SR.fig1_strength(X[smodel["wc_col"]], cement_type=smodel["cement_type"])
        y = X["fc_mpa"].to_numpy(float) - np.asarray(base, float)
        mu_before, _ = SR.predict_strength_mpa(smodel, X, kind="sample")
        rep["strength_errors"] = [{"trial_id": t, "predicted_mpa": float(p), "measured_mpa": float(m)}
                                  for t, p, m in zip(X["trial_id"], mu_before, X["fc_mpa"])]
        smodel = condition(smodel, X, y, X["batch_key"], f"{len(X)} P1-PPC lab batches")
    return wmodel, smodel, rep


def read_all_logs(pattern="*PPC_results_log.csv"):
    """Every PPC results log in the folder (P1 M30/M35, M10/M15, ...). The models learn from
    ALL measured batches, whichever notebook planned them."""
    from pathlib import Path
    parts = [read_log(str(p)) for p in sorted(Path(".").glob(pattern))]
    parts = [p for p in parts if len(p)]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
