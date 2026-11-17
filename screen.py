"""Achievability check and the exhaustive code-legal screen.

GENERATED FILE - do not edit. Edit 11_achievability_and_screen.ipynb and re-run its export cell.

Only three knobs are searched: binder, SCM split, admixture dose. Water and the
aggregate split are computed by layer0 from IS 10262. The space is therefore small
enough to enumerate exactly, which is deterministic (gate G7).

SERVE rejects points outside training support; EXPLORE keeps and flags them.
Standards constraints are identical in both modes.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

import is_rules as IS
import layer0 as L0
import workability_residual as WR
import strength_residual as SR

def load_strength_model(path="strength_residual_model.joblib"):
    """Load the strength model notebook 10b fits. Never fabricate one.

    The older strength_model.joblib in this repository exposes no predict() and no
    'gp' key -- it is a dict of {target, members, noise, q90, feature_range, n_groups}
    and has never been usable here. It is not loaded.
    """
    p = Path(path)
    if not p.exists():
        print(f"[fail-safe] {path} not found -- run 10b_strength_residual_GP.ipynb first")
        return None
    try:
        m = joblib.load(p)
    except Exception as e:
        print(f"[fail-safe] {path} present but did not load: {type(e).__name__}: {e}")
        return None
    need = {"gp", "scaler", "features", "noise_var", "wc_col", "cement_type"}
    missing = need - set(m) if isinstance(m, dict) else need
    if missing:
        print(f"[fail-safe] {path} is missing {sorted(missing)}; treating as absent")
        return None
    return m


def predict_strength(smodel, rows, target_mean_mpa, kind="sample"):
    """Predicted 28-day strength, its sd, and P(reaching the target mean strength).

    kind='sample' by default: [IS] IS 456 cl 15.3 makes a SAMPLE the mean of three
    specimens, and that is the quantity acceptance is judged on (cl 16), so it is the
    one the feasibility threshold should use. Asking the 'mean' question instead would
    understate the risk; asking 'specimen' would overstate it.

    Returns (mu, sd, p) or (None, None, None) when no model is available. Returning
    None is deliberate: a candidate whose strength cannot be predicted is NOT_VERIFIED,
    and NOT_VERIFIED on a hard check must stop the mix rather than be replaced by an
    optimistic guess.
    """
    if smodel is None:
        return None, None, None
    try:
        mu, sd = SR.predict_strength_mpa(smodel, rows, kind=kind)
        p = SR.p_meets_target(smodel, rows, target_mean_mpa, kind=kind)
        return mu, sd, p
    except SR.CurveNotDigitised as e:
        print(f"[fail-safe] {e}")
        return None, None, None
    except Exception as e:
        print(f"[fail-safe] strength prediction failed: {type(e).__name__}: {e}")
        return None, None, None


def achievability_report(req, state, *, wmodel, candidates=None,
                         out_of_group_sd_mm=None, out_of_group_bias_mm=None,
                         tolerance_mm=None, confidence=0.90):
    """[PC] Can the requested slump band be held? Answer in words, before any search.

    There are TWO ways to miss and they need separate answers:
      OFFSET -- the predicted mean is already outside the band (bias)
      WIDTH  -- the band is narrower than the model's own uncertainty (variance)

    An earlier version tested only WIDTH and never touched the model, so a mix
    predicted 156 mm off target was reported as a 38 mm uncertainty problem.
    `candidates` is therefore required whenever a mean-offset verdict is wanted;
    without it only the WIDTH question can be answered and the result says so.

    tolerance_mm None -> take the IS band for the specified slump via
    is_rules.slump_acceptance_band. A caller may override, but may not widen
    silently: the value used is returned.
    """
    from scipy.stats import norm

    oog_sd = float(out_of_group_sd_mm if out_of_group_sd_mm is not None
                   else wmodel["out_of_group_sd_mm"])
    oog_bias = float(out_of_group_bias_mm if out_of_group_bias_mm is not None
                     else wmodel.get("out_of_group_bias_mm", 0.0))
    band = None
    if tolerance_mm is None:
        try:
            band = IS.slump_acceptance_band(req.target_slump_mm)
            tolerance_mm = float(band.get("tolerance_mm") or band.get("plus_minus_mm"))
        except Exception:
            tolerance_mm = 25.0
            band = {"source": "[PC] caller default, no IS band resolved"}

    z = norm.ppf(0.5 + confidence / 2.0)
    half_width = z * oog_sd
    width_ok = half_width <= tolerance_mm

    out = {
        "target_slump_mm": req.target_slump_mm,
        "tolerance_mm": tolerance_mm,
        "tolerance_source": band,
        "confidence": confidence,
        "out_of_group_sd_mm": oog_sd,
        "out_of_group_bias_mm": oog_bias,
        "half_width_mm": half_width,
        "width_ok": bool(width_ok),
    }

    if candidates is None or len(candidates) == 0:
        out.update({
            "offset_checked": False,
            "achievable": bool(width_ok),
            "message": (
                (f"WIDTH only: a +/-{tolerance_mm:.0f} mm band is inside the model's "
                 f"{half_width:.0f} mm half-width at {confidence:.0%}. The mean OFFSET "
                 f"has not been checked -- no candidates were supplied.")
                if width_ok else
                (f"NOT achievable -- WIDTH: the requested band is +/-{tolerance_mm:.0f} mm "
                 f"but the model's half-width at {confidence:.0%} is {half_width:.0f} mm, "
                 f"measured leave-one-group-out. The mean OFFSET has not been checked.")),
        })
        return out

    a = WR.achievable(wmodel, candidates, target_slump_mm=req.target_slump_mm,
                      tolerance_mm=tolerance_mm, confidence=confidence,
                      out_of_group_sd_mm=oog_sd, out_of_group_bias_mm=oog_bias)
    n_ok = int(np.sum(a["achievable"]))
    best = int(np.argmin(a["offset_from_target_mm"]))
    out.update({
        "offset_checked": True,
        "n_candidates_checked": len(candidates),
        "n_achievable": n_ok,
        "best_offset_mm": float(a["offset_from_target_mm"][best]),
        "best_predicted_mm": float(np.atleast_1d(a["predicted_mean_mm"])[best]),
        "achievable": bool(n_ok > 0),
        "message": (
            f"{n_ok} of {len(candidates)} candidates can hold +/-{tolerance_mm:.0f} mm "
            f"at {confidence:.0%}."
            if n_ok else
            f"NOT achievable: none of {len(candidates)} candidates can hold "
            f"+/-{tolerance_mm:.0f} mm at {confidence:.0%}. Closest predicted mean is "
            f"{float(np.atleast_1d(a['predicted_mean_mm'])[best]):.0f} mm, "
            f"{float(a['offset_from_target_mm'][best]):.0f} mm from target; the model's "
            f"half-width is {half_width:.0f} mm and an unseen family's centre moves a "
            f"further {oog_bias:.0f} mm. {a['verdict'][best]}"),
        "per_candidate_verdict": a["verdict"],
    })
    return out


GRID = {
    # [PC] project design choice; declared here, printed on every run, recorded per candidate
    "binder_step_kg": 10.0,
    "scm_step": 0.025,        # fine enough to reach the 7-14 percent band this plant uses
    "admixture_step_pct": 0.1,
    # [PC] Section 2 SCM search ceilings. NOT standards limits -- see legal_grid().
    # 0.35 for fly ash aligns the search with the largest share IS 456 Table 5 Note 1
    # can ever count, so the optimiser is not searching where the gate must refuse.
    "flyash_max_frac": 0.35,
    "ggbs_max_frac": 0.50,
}

# [IS] The ONLY 450 kg/m3 limit is IS 456:2000 cl 8.2.4.2, on CEMENT, fly ash and GGBS
#      excluded (is_rules.IS456_CL_8_2_4_2_MAX_CEMENT; is_rules fixture
#      test_450_caps_cement_only_not_cementitious; IS 10262 Annex D checks 428 kg OPC in a
#      535 kg binder against it and nothing else). The project follows the IS limit only,
#      as decided by the project owner: an earlier version of this notebook also capped
#      TOTAL cementitious at 450 as a project constraint. That cap is removed. It would
#      have refused the IS 10262 cl 5.8 trial at w/cm -10 % for most designs here.
#
# What bounds the binder from above is therefore: the cement ceiling (IS), and -- for
# what may be served or explored -- the data the models were fitted on ([PC] below).

# [PC] EXPLORE trust region. A proposal for a PHYSICAL trial must sit near what the
#      models have seen: each support-box axis is widened by this fraction of its own
#      width, and nothing outside is proposed. SERVE uses the unwidened box.
EXPLORE_MARGIN_FRAC = 0.10


def legal_grid(req, state, *, grid=None, binder_lo=None, binder_hi=None):
    """Every combination of the three free knobs that the standards allow.

    Bounds come from the standards, not from a notebook constant:
      binder low   [IS] IS 456 Table 5 minimum cementitious for the exposure
      binder high  [IS] IS 456 cl 8.2.4.2 -- 450 kg/m3 of CEMENT; because fly ash and
                   GGBS are excluded, the binder ceiling rises with the SCM share
      SCM shares   [IS] IS 10262 Table 9 dosage ranges, plus zero
      admixture    [IS] IS 9103 cl 10.2 manufacturer range; zero if none declared
    """
    grid = {**GRID, **(grid or {})}
    t5 = IS.table5_lookup(req.exposure, req.use, int(state.msa_mm))
    lo = binder_lo if binder_lo is not None else float(t5["min_cement_kg_m3"])

    # ---- SCM search range -------------------------------------------------------
    # [PC] IS 10262 Table 9 (cl 6.2.6) is NOT the authority here, for two reasons:
    #   1. it belongs to SECTION 3, high-strength concrete (M65 and above). This order
    #      routes through route_domain() to ORDINARY, i.e. Section 2.
    #   2. is_rules records its status as GUIDANCE, and GUIDANCE is not in BINDING
    #      ({verified, project_constraint}), so it may not act as a hard bound at all.
    # An earlier version of this grid used it as a hard bound on an M30 mix. That was
    # wrong on both counts, and it is what made SERVE structurally empty: Table 9's
    # fly-ash range starts at 15 percent while this plant has only ever run 7-14.
    #
    # For Section 2 the binding limits are: IS 456 cl 8.2.4.2 on CEMENT, and IS 456
    # Table 5 Note 1 on how much fly ash may COUNT toward the minimum binder and the
    # free w/c -- both already enforced by compliance_gate. The SEARCH range is
    # therefore a declared project choice.
    domain = IS.route_domain(req.grade)
    if str(getattr(domain, "value", domain)) == "C":
        fa_lo, fa_hi = IS.IS10262_TABLE9_SCM_DOSAGE_PCT["fly_ash"]
        gg_lo, gg_hi = IS.IS10262_TABLE9_SCM_DOSAGE_PCT["ggbs"]
        fa_opts = [0.0] + list(np.arange(fa_lo / 100.0, fa_hi / 100.0 + 1e-9, grid["scm_step"]))
        gg_opts = [0.0] + list(np.arange(gg_lo / 100.0, gg_hi / 100.0 + 1e-9, grid["scm_step"]))
        scm_basis = ("IS 10262 Table 9 (cl 6.2.6), Section 3 high strength -- [GUIDANCE], "
                     "used here only because the grade routes to that section")
    else:
        fa_hi = grid["flyash_max_frac"]
        gg_hi = grid["ggbs_max_frac"]
        fa_opts = list(np.arange(0.0, fa_hi + 1e-9, grid["scm_step"]))
        gg_opts = list(np.arange(0.0, gg_hi + 1e-9, grid["scm_step"]))
        scm_basis = ("[PC] project search range for Section 2; the binding limits are "
                     "IS 456 cl 8.2.4.2 (cement) and Table 5 Note 1 (countable fly ash), "
                     "both enforced by compliance_gate, not by this range")
    if "flyash" not in state.scms_available:
        fa_opts = [0.0]
    if "ggbs" not in state.scms_available:
        gg_opts = [0.0]

    rng = state.admixture_dosage_range_pct
    adm_opts = ([0.0] if rng is None
                else list(np.arange(rng[0], rng[1] + 1e-9, grid["admixture_step_pct"])))

    combos = []
    for fa, gg in itertools.product(fa_opts, gg_opts):
        if fa + gg >= 1.0:
            continue
        # [IS] cl 8.2.4.2 caps CEMENT at 450: cement = binder x (1 - fa - gg), so the
        #      cement ceiling allows binder up to 450/(1-fa-gg).
        is_ceiling = IS.IS456_CL_8_2_4_2_MAX_CEMENT / (1.0 - fa - gg)
        hi = binder_hi if binder_hi is not None else is_ceiling
        for b in np.arange(lo, hi + 1e-9, grid["binder_step_kg"]):
            for a in adm_opts:
                combos.append({"binder_kg_m3": float(b), "flyash_frac": float(fa),
                               "ggbs_frac": float(gg), "admixture_pct_of_binder": float(a)})
    return combos, {"grid": grid, "binder_lo": lo, "domain": str(domain),
                    "scm_range_basis": scm_basis,
                    "binder_hi_rule": "IS 456 cl 8.2.4.2 cement ceiling 450 / (1 - SCM share)",
                    "flyash_options": [round(x, 4) for x in fa_opts],
                    "ggbs_options": [round(x, 4) for x in gg_opts],
                    "admixture_options": [round(x, 4) for x in adm_opts],
                    "n_combinations": len(combos)}


def training_support(train_df, features):
    """[PC] The box the models have actually seen.

    Crude on purpose: it must be explainable to a plant engineer, and a convex hull
    in seven dimensions is not.

    Takes the TRAINING FRAME, not the model -- an earlier version accepted either and
    silently returned None for a model, after which SERVE accepted everything.
    """
    if not isinstance(train_df, pd.DataFrame):
        raise TypeError(
            f"training_support needs the training DataFrame, got {type(train_df).__name__}. "
            "Passing the model returns no box, and a missing box makes SERVE accept "
            "every candidate.")
    missing = [f for f in features if f not in train_df]
    if missing:
        raise ValueError(f"training frame has no column for {missing}; the support box "
                         f"would silently omit those axes.")
    return {f: (float(train_df[f].min()), float(train_df[f].max())) for f in features}


def inside_support(row, support, tol=0.0):
    """True / False. Never None.

    A missing or NaN feature is OUTSIDE support, not unknown-and-therefore-fine.
    The project's fail-safe rule is that missing information rejects; returning None
    here (as an earlier version did) made SERVE fail OPEN, because `None != False`.
    """
    if not support:
        raise ValueError("no support box supplied -- refusing to judge membership")
    for f, (lo, hi) in support.items():
        v = row.get(f)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return False
        if not (lo - tol <= v <= hi + tol):
            return False
    return True


def screen(req, state, *, wmodel, smodel=None, support=None, mode="serve",
           grid=None, out_of_group_sd_mm=None, confidence=0.90,
           tolerance_mm=None, max_candidates=None, mixes=None):
    """The exhaustive legal screen. Returns (DataFrame, meta).

    mode='serve'   -> reject anything outside training support
    mode='explore' -> keep it, flagged, because that is where a trial teaches most

    Standards constraints are IDENTICAL in both modes. Exploration widens where the
    models may be asked to predict. It never widens what IS 456 permits.
    """
    if mode not in ("serve", "explore", "score"):
        raise ValueError("mode must be 'serve', 'explore' or 'score'")
    if (mode == "score") != (mixes is not None):
        raise ValueError("mode='score' scores the supplied `mixes` (Layer 0 MixDesign "
                         "objects, e.g. an IS 10262 cl 5.8 trial set) and nothing else")
    from scipy.stats import norm

    oog = float(out_of_group_sd_mm if out_of_group_sd_mm is not None
                else wmodel["out_of_group_sd_mm"])

    # [V] The cl 5.3 admixture water reduction, fitted in notebook 10 from this plant's
    #     own families. This is what COUPLES the admixture knob to water: more
    #     superplasticiser -> less water -> less binder at the same w/c -> different
    #     aggregate split. Without it the dose moves nothing upstream, which is what put
    #     every candidate 30 kg above any water the plant has ever batched.
    wfit = wmodel.get("water_reduction_fit")
    if wfit is None:
        raise ValueError(
            "the workability model carries no water_reduction_fit. Re-run notebook 10: "
            "without it Layer 0 has no cl 5.3 reduction to apply and every candidate is "
            "designed at a water content no real batch uses.")

    if mixes is None:
        combos, gmeta = legal_grid(req, state, grid=grid)
    else:
        combos = [{"_mix": m, "binder_kg_m3": m.binder_kg_m3,
                   "flyash_frac": m.flyash_kg_m3 / m.binder_kg_m3,
                   "ggbs_frac": m.ggbs_kg_m3 / m.binder_kg_m3,
                   "admixture_pct_of_binder": 100.0 * m.admixture_kg_m3 / m.binder_kg_m3}
                  for m in mixes]
        gmeta = {"grid": "supplied mixes (mode='score')", "n_combinations": len(combos)}
    rows, refused, diagnostic = [], {}, {}

    for c in combos:
        if "_mix" in c:
            m = c["_mix"]
        else:
            # the reduction depends on THIS candidate's dose, so the requirement is
            # rebuilt per candidate rather than fixed per order
            req_c = replace(req, water_reduction_pct=float(
                WR.water_reduction_pct(c["admixture_pct_of_binder"], wfit)))
            try:
                m = L0.design_mix(req_c, state, binder_kg_m3=c["binder_kg_m3"],
                                  flyash_frac=c["flyash_frac"], ggbs_frac=c["ggbs_frac"],
                                  admixture_pct_of_binder=c["admixture_pct_of_binder"])
            except Exception as e:
                refused[f"design: {type(e).__name__}"] = refused.get(
                    f"design: {type(e).__name__}", 0) + 1
                continue
        if not m.decided:
            key = "gate: " + (m.gate.get("hard_not_verified") or
                              [ck["check"] for ck in m.gate["checks"]
                               if ck["outcome"] in ("fail", "override_required")] or ["?"])[0]
            refused[key] = refused.get(key, 0) + 1
            continue

        r = {
            "cement_kg_m3": m.cement_kg_m3, "flyash_kg_m3": m.flyash_kg_m3,
            "ggbs_kg_m3": m.ggbs_kg_m3, "water_kg_m3": m.water_kg_m3,
            "admixture_kg_m3": m.admixture_kg_m3, "binder_kg_m3": m.binder_kg_m3,
            "fine_agg_kg_m3": m.fine_agg_kg_m3, "coarse_agg_kg_m3": m.coarse_agg_kg_m3,
            "crushed_sand_kg_m3": m.fine_agg_kg_m3 if state.sand_type == "crushed" else 0.0,
            "natural_sand_kg_m3": 0.0 if state.sand_type == "crushed" else m.fine_agg_kg_m3,
            "wb_ratio": m.wc_ratio, "free_water_for_gate": m.water_kg_m3,
            "sp_pct_binder": c["admixture_pct_of_binder"],
            # MASS fraction, matching how both training datasets define this column.
            # The VOLUME fraction (Table 5 basis) is kept separately below.
            "fine_frac_of_agg": m.fine_mass_frac_of_agg,
            "fine_vol_frac": m.fine_frac_of_agg,
            "scm_frac": (m.flyash_kg_m3 + m.ggbs_kg_m3) / max(m.binder_kg_m3, 1e-9),
            "msand_frac": 1.0 if state.sand_type == "crushed" else 0.0,
            "agg_binder_ratio": (m.fine_agg_kg_m3 + m.coarse_agg_kg_m3) / max(m.binder_kg_m3, 1e-9),
            "concrete_temp": (np.nan if req.concrete_temp_c is None
                              else float(req.concrete_temp_c)),
            "water_reduction_pct": m.water_reduction_pct,
            "water_before_reduction_kg_m3": m.water_before_reduction_kg_m3,
            "wc_counted": m.wc_counted,
            "counted_binder_kg_m3": m.counted_binder_kg_m3,
            "admixture_water_kg_m3": m.admixture_water_kg_m3,
            "scm_combination": "+".join(IS.scm_combination(state.cement_type, m.flyash_kg_m3,
                                                            m.ggbs_kg_m3)[1]) or "none",
            "sources_verified": m.sources_verified,
            "msa": m.msa_mm, "volume_m3": m.volume_closure_m3,
            "dv_binder_kg_m3": c["binder_kg_m3"], "dv_flyash_frac": c["flyash_frac"],
            "dv_ggbs_frac": c["ggbs_frac"], "dv_sp_pct_binder": c["admixture_pct_of_binder"],
            "dv_wb_ratio": m.wc_ratio, "dv_fine_frac_of_agg": m.fine_mass_frac_of_agg,
            "target_mean": m.target_mean_strength, "grade": m.grade,
            "sand_zone": m.sand_zone, "state_hash": m.state_hash,
            "gate_pass": m.gate["pass"], "gate_decided": m.decided,
            "gate_hard_not_verified": ";".join(m.gate.get("hard_not_verified") or []),
            "status": L0.ValidationLevel.COMPUTATIONALLY_COMPLIANT.name,
        }
        rows.append(r)

    if not rows:
        ach = achievability_report(req, state, wmodel=wmodel, candidates=None,
                                   out_of_group_sd_mm=oog, tolerance_mm=tolerance_mm,
                                   confidence=confidence)
        return pd.DataFrame(), {"achievability": ach, "grid": gmeta,
                                "refused_exclusive": refused,
                                "refused_diagnostic": diagnostic,
                                "n_combinations": gmeta["n_combinations"],
                                "mode": mode, "n_candidates": 0,
                                "out_of_group_sd_mm": oog}

    df = pd.DataFrame(rows)
    # Temperature is a PLANT reading, not a design value. Until an order carries one,
    # candidates are evaluated at the training median that notebook 10 now stores, so
    # the model is queried inside its own range rather than at NaN or at a guess.
    # (An earlier version wrote `... if False else 30.0` -- a dead branch and a
    # hardcoded number that happened to sit inside the support box and so passed the
    # guard it should have tripped.)
    for f in wmodel["features"]:
        if f in df and df[f].isna().all():
            med = wmodel.get("feature_median", {}).get(f)
            if med is None:
                raise ValueError(
                    f"candidate feature {f!r} is unset and notebook 10 stored no median "
                    f"for it. Supply it per order or re-run notebook 10.")
            df[f] = med
            df[f + "_source"] = "training median (not an order value)"

    # ---- workability ----------------------------------------------------------
    mu_s, sd_in = WR.predict_slump(wmodel, df, kind="mean")
    sd_s = np.maximum(sd_in, oog)                      # honest scale, see notebook 10
    z = norm.ppf(0.5 + confidence / 2.0)
    df["slump_pred"] = mu_s
    df["slump_sd"] = sd_s
    df["slump_lo90"] = mu_s - z * sd_s
    df["slump_hi90"] = mu_s + z * sd_s
    # the acceptance band, resolved once: [IS] is_rules.slump_acceptance_band when the
    # caller supplies no tolerance, else the caller's own value
    if tolerance_mm is None:
        try:
            _b = IS.slump_acceptance_band(req.target_slump_mm)
            tol = float(_b.get("tolerance_mm") or _b.get("plus_minus_mm"))
        except Exception:
            tol = 25.0
    else:
        tol = float(tolerance_mm)
    lo_t, hi_t = req.target_slump_mm - tol, req.target_slump_mm + tol
    df["P_slump"] = norm.cdf((hi_t - mu_s) / sd_s) - norm.cdf((lo_t - mu_s) / sd_s)

    # ---- strength -------------------------------------------------------------
    # the strength model needs wb_ratio under its own column name
    if smodel is not None and smodel["wc_col"] not in df:
        df[smodel["wc_col"]] = df["wb_ratio"]
    # MATERIAL-SPECIFIC input: the cement lot's 28-day strength from its certificate.
    # Used when supplied; only otherwise does the strength model fall back to a median.
    if state.cement_28d_strength is not None:
        df["cement_28d_strength"] = float(state.cement_28d_strength)
        df["cement_28d_strength_source"] = "MaterialState (cement certificate)"
    # fill any strength feature the candidate frame does not carry, from the fit medians
    if smodel is not None:
        for f in smodel["features"]:
            if f not in df or df[f].isna().all():
                med = smodel.get("feature_median", {}).get(f)
                if med is None:
                    raise ValueError(f"strength feature {f!r} is unset and 10b stored no "
                                     f"median for it")
                df[f] = med
                df[f + "_source"] = "strength training median (not an order value)"

    mu_f, sd_f, p_f = predict_strength(smodel, df, df["target_mean"].to_numpy(float))
    if mu_f is None:
        df["fc_pred"] = np.nan
        df["fc_sd"] = np.nan
        df["P_strength"] = np.nan
        df["strength_status"] = "NOT_VERIFIED -- no usable strength model loaded"
    else:
        df["fc_pred"] = mu_f
        df["fc_sd"] = sd_f
        df["P_strength"] = p_f
        df["strength_status"] = (f"predicted [IS] IS 456 cl 15.3 sample (mean of 3); "
                                 f"Fig 1 baseline on {smodel['cement_type']}")
        # [PC] w/c outside the range the strength model was fitted on is extrapolation
        lo, hi = smodel["wc_range"]
        ok = (df["wb_ratio"] >= lo) & (df["wb_ratio"] <= hi)
        df["inside_strength_wc_range"] = ok
        if not ok.all():
            diagnostic[f"strength fit: w/c outside [{lo:.3f}, {hi:.3f}]"] = int((~ok).sum())

    # ---- support guard --------------------------------------------------------
    if support:
        df["inside_training_range"] = df.apply(lambda r: inside_support(r, support), axis=1)
    else:
        df["inside_training_range"] = None

    # [PC] The support box covers the GP's seven features. Water is deliberately NOT one
    #      of them -- that is what makes G1 hold by construction -- so the box does not
    #      guard it. But the cl 5.3 reduction relation SETS the water for every candidate
    #      and was fitted inside a narrow band. Outside that band it extrapolates, and
    #      nothing else would notice.
    rng = WR.inside_fitted_range(wfit, sp_pct=df["sp_pct_binder"].to_numpy(float),
                                 water_kg_m3=df["water_kg_m3"].to_numpy(float))
    ok_w = np.asarray(rng["water_kg_m3"], dtype=bool)
    ok_sp = np.asarray(rng["sp_pct_binder"], dtype=bool)
    df["inside_water_fit_range"] = ok_w
    df["inside_sp_fit_range"] = ok_sp
    df["inside_fitted_ranges"] = ok_w & ok_sp
    if not ok_w.all():
        diagnostic[f"cl 5.3 fit: water outside "
                   f"[{rng['water_kg_m3_range'][0]:.1f}, {rng['water_kg_m3_range'][1]:.1f}] kg"] = \
            int((~ok_w).sum())
    if not ok_sp.all():
        diagnostic[f"cl 5.3 fit: SP dose outside "
                   f"[{rng['sp_pct_binder_range'][0]:.3f}, {rng['sp_pct_binder_range'][1]:.3f}] %"] = \
            int((~ok_sp).sum())

    if mode == "serve":
        before = len(df)
        if support:
            # WHY did support refuse? a bare zero is not an answer. These are
            # DIAGNOSTIC counts over the same rows, so they overlap and must never be
            # added to the exclusive cause counts -- hence the separate prefix.
            for f, (flo, fhi) in support.items():
                if f in df:
                    n_out = int(((df[f] < flo) | (df[f] > fhi)).sum())
                    if n_out:
                        diagnostic[f"support axis: {f} outside [{flo:.3g}, {fhi:.3g}]"] = n_out
        df = df[df["inside_training_range"] == True].copy()
        refused["support: outside the training box"] = before - len(df)
        # SERVE must not ship a mix whose water the cl 5.3 relation never saw
        before2 = len(df)
        df = df[df["inside_fitted_ranges"] == True].copy()
        n_fit = before2 - len(df)
        if n_fit:
            refused["support: outside the cl 5.3 fitted water / dose range"] = n_fit
        if "inside_strength_wc_range" in df:
            before3 = len(df)
            df = df[df["inside_strength_wc_range"] == True].copy()
            n_s = before3 - len(df)
            if n_s:
                refused["support: outside the Fig 1 fitted w/c range"] = n_s

    if mode == "explore" and support:
        # [PC] trust region for physical trials -- see EXPLORE_MARGIN_FRAC
        wide = {f: (lo - EXPLORE_MARGIN_FRAC * (hi - lo), hi + EXPLORE_MARGIN_FRAC * (hi - lo))
                for f, (lo, hi) in support.items()}
        df["inside_trust_region"] = df.apply(lambda r: inside_support(r, wide), axis=1)
        before = len(df)
        df = df[df["inside_trust_region"] == True].copy()
        refused[f"explore: outside the trust region (support +/-{EXPLORE_MARGIN_FRAC:.0%})"] = \
            before - len(df)

    df["mode"] = mode
    if max_candidates:
        df = df.head(int(max_candidates)).copy()

    ach = achievability_report(req, state, wmodel=wmodel,
                               candidates=df if len(df) else None,
                               out_of_group_sd_mm=oog, tolerance_mm=tol,
                               confidence=confidence)
    df["achievable_band"] = ach["achievable"]

    return df.reset_index(drop=True), {
        "achievability": ach, "grid": gmeta,
        "refused_exclusive": refused,          # one cause per combo; these SUM
        "refused_diagnostic": diagnostic,      # overlapping; these do NOT sum
        "n_combinations": gmeta["n_combinations"],
        "n_after_gate": gmeta["n_combinations"] - sum(refused.values()) + len(df) - len(df),
        "mode": mode, "n_candidates": len(df), "out_of_group_sd_mm": oog}


def _median(s):
    v = pd.to_numeric(s, errors="coerce").dropna()
    return float(v.median()) if len(v) else None


def _mode(s):
    v = s.dropna().astype(str).str.strip()
    v = v[v != ""]
    return v.mode().iloc[0] if len(v) else None


EXPOSURE = {"mild": IS.Exposure.MILD, "moderate": IS.Exposure.MODERATE,
            "severe": IS.Exposure.SEVERE, "very severe": IS.Exposure.VERY_SEVERE,
            "very_severe": IS.Exposure.VERY_SEVERE, "extreme": IS.Exposure.EXTREME}
USE = {"RCC": IS.UseClass.RCC, "PCC": IS.UseClass.PCC}

# [PC] How many batches with 28-day cube results make 'satisfactory data on suitability'
#      (IS 456 cl 5.1) for an 'other combination'. IS 456 prints no number. 30 mirrors
#      the 30 results IS 10262 cl 4.2.1.1 asks for before a standard deviation is
#      'established' -- an analogy, recorded as a project choice, not an IS rule.
SUITABILITY_MIN_BATCHES = 30


def suitability_evidence_from_data(g, cement_type, scms):
    """[EI] IS 456 cl 5.1 -- 'satisfactory data on their suitability, such as performance
    tests on concrete containing them'. Counts batches of THIS plant (all grades) made with
    the same cement type and the same added mineral admixtures that carry three 28-day
    cube results."""
    if not scms:
        return None
    m = g["cement_type"].astype(str).str.upper().eq(str(cement_type).upper())
    for name, col in (("flyash", "flyash_kg_m3"), ("ggbs", "ggbs_kg_m3")):
        has = pd.to_numeric(g[col], errors="coerce").fillna(0).gt(0)
        m &= has if name in scms else ~has
    cubes = g[[c for c in ("cube_28d_1", "cube_28d_2", "cube_28d_3") if c in g]].notna().sum(axis=1) >= 3
    n = int((m & cubes).sum())
    if n < SUITABILITY_MIN_BATCHES:
        return None
    plant = _mode(g.loc[m, "plant_lab_id"]) if "plant_lab_id" in g else "?"
    src = _mode(g.loc[m, "source_file"]) if "source_file" in g else "?"
    return (f"{n} production batches with three 28-day cubes each, plant {plant} "
            f"({src}), {cement_type} + {'+'.join(scms)} [EI: IS 456 cl 5.1 performance "
            f"tests; threshold {SUITABILITY_MIN_BATCHES} batches is a project choice]")


def plant_orders(path="04_workability_dataset.csv", *, flyash_sg, admixture_range_pct):
    """One order + MaterialState per real design family in the dataset.

    flyash_sg and admixture_range_pct are NOT in the dataset; the caller declares them.
    Refuses rather than guesses: a family missing exposure, use, slump or msa is skipped
    with the reason.
    """
    d = pd.read_csv(path)
    d = d[d["design_grp"].astype(str).str.contains("[A-Za-z]", na=False)]
    out = []
    for fam, g in d.groupby("design_grp"):
        grade = _mode(g["grade"])
        exp = (_mode(g["exposure"]) or "").lower()
        use = (_mode(g["concrete_use"]) or "").upper()
        slump = _median(g["target_slump"])
        msa = _median(g["msa"])
        missing = [n for n, v in (("grade", grade), ("exposure", EXPOSURE.get(exp)),
                                  ("use", USE.get(use)), ("target_slump", slump),
                                  ("msa", msa)) if v is None]
        if missing:
            out.append({"family": fam, "error": f"dataset does not record {missing}"})
            continue
        placing = g["placing_method"].astype(str).str.lower()
        pumped = bool((placing.str.contains("pump")).mean() > 0.5)
        cement = (_mode(g["cement_type"]) or "").upper()
        sand = "crushed" if "m-sand" in (_mode(g["sand_type"]) or "").lower() else "natural"
        scms = tuple(s for s, col in (("flyash", "flyash_kg_m3"), ("ggbs", "ggbs_kg_m3"))
                     if pd.to_numeric(g[col], errors="coerce").fillna(0).gt(0).any())
        a20, a10 = _median(g["agg_20mm"]), _median(g["agg_10mm"])
        state = L0.MaterialState(
            cement_type=cement,
            cement_sg=_median(g["cement_sg"]),
            cement_28d_strength=_median(g["cement_28d_strength"]),
            flyash_sg=flyash_sg if "flyash" in scms else None,
            sand_type=sand,
            sand_sg=_median(g["sand_sg"]),
            sand_absorption_pct=_median(g["sand_absorption"]),
            sand_passing_600um=_median(g["sand_pass_600"]),
            ca_sg=_median(g["ca_sg"]),
            ca_shape="angular",
            ca_absorption_pct=_median(g["ca_absorption"]),
            msa_mm=msa,
            scms_available=scms,
            admixture_sg=_median(g["admixture_sg"]),
            admixture_solids_pct=_median(g["admixture_solids"]),
            admixture_dosage_range_pct=admixture_range_pct,
            # the evidence is about the COMBINATION at this plant, not about one grade:
            # count every batch of the same plant, all families
            combination_suitability_evidence=suitability_evidence_from_data(
                d[d["plant_lab_id"].astype(str) == str(_mode(g["plant_lab_id"]))], cement, scms),
            ca_split_20_10=(a20, a10) if a20 and a10 else None,
        )
        req = L0.Requirement(
            grade=grade, target_slump_mm=slump, exposure=EXPOSURE[exp], use=USE[use],
            pumpable=pumped, pumpable_reduction_frac=1.0,
            concrete_temp_c=_median(g["concrete_temp"]),
        )
        plant = {"plant_binder": _median(g["binder_kg_m3"]),
                 "plant_flyash": _median(g["flyash_kg_m3"]),
                 "plant_water": _median(g["water_kg_m3"]),
                 "plant_wb": _median(g["wb_ratio"]),
                 "plant_sp_pct": _median(g["sp_pct_binder"]),
                 "plant_slump_measured": _median(g["slump_mm"]),
                 "sand_moisture_median": _median(g["sand_moisture"]),
                 "ca_moisture_median": _median(g["ca_moisture"]),
                 "plant_lab_id": _mode(g["plant_lab_id"]),
                 "source_file": _mode(g["source_file"])}
        out.append({"family": fam, "req": req, "state": state, "plant": plant,
                    "n_batches": len(g), "pumped": pumped})
    return out
