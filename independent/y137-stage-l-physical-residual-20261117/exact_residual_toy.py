#!/usr/bin/env python3
"""Y137 Stage L: exact full-physical residual plumbing on a weighted toy.

Production obligation: certify full-H residual norm of actual low Ritz
witnesses in the full 3x4 S3 gauge-orbit metric, including K5 boundary.
An arbitrary Galerkin witness is supported on at most 654651 original
physical coordinates (8 flats, all 8034 K2, all 147344 K3, 499265
touched K4), requiring at most 47134872 original 72-move input actions.

This file is a SMALL TOY/acceptance-spec test. It does not calculate a
new 3x4 Ritz eigenvector, source output or positive Wilson weight.
Every numerical operation in the test uses exact integers.
"""
import hashlib
import sys

W=(1,2,3,6,6)
MAG=(0,1,2,3,4)
ADJ=(
    {0:64,1:2,3:6},
    {0:1,1:68,2:3},
    {1:2,2:68,3:2},
    {0:1,2:1,3:69,4:1},
    {3:1,4:71},
)
D=10
Z=700
N=5
# Old physical trial subspace: flat coordinate e0 and a noncoordinate
# Krylov-like column e1+e2; new column e3 is metric-orthogonal.
BASIS=(
    (1,0,0,0,0),
    (0,1,1,0,0),
    (0,0,0,1,0),
)
COEFF=(4,-2,3)
WIND=(0,1,4,9,14)


def require(ok,reason):
    if not ok:
        print("Y137_L_TOY_REFUSE|reason="+reason+"|json=0",flush=True)
        raise SystemExit(1)


def emit(label,**fields):
    print(label+"|"+"|".join(str(k)+"="+str(v)
         for k,v in fields.items())+"|json=0",flush=True)


def digest(value):
    return hashlib.sha256(str(value).encode("ascii")).hexdigest()


def validate_source(graph):
    require(len(graph)==N,"toy_wrong_graph_dim")
    for i,row in enumerate(graph):
        require(sum(row.values())==72,"toy_non_72_move_source")
        for j,count in row.items():
            require(j in range(N) and count>=0,"toy_invalid_edge")
            require(W[i]*count==W[j]*graph[j].get(i,0),
                    "toy_weighted_reverse_edge_forged")


def weighted_inner(x,y):
    return sum(W[i]*x[i]*y[i] for i in range(N))


def direct_action(amplitudes,graph):
    return tuple((72+9*MAG[i])*amplitudes[i]
          -sum(count*amplitudes[j] for j,count in graph[i].items())
          for i in range(N))


def scatter_action(amplitudes,graph,skip_exterior=False):
    # In the real physical source, the target set must be formed from
    # every supported input orbit's original canonical electric neighbors.
    occupied={i for i,x in enumerate(amplitudes) if x}
    targets=set(occupied)
    flux={}
    moves=0
    for i in sorted(occupied):
        for j,count in graph[i].items():
            moves+=count
            if skip_exterior and j not in occupied:
                continue
            targets.add(j)
            flux[j]=flux.get(j,0)+W[i]*count*amplitudes[i]
    action=[0]*N
    for j in sorted(targets):
        incoming=flux.get(j,0)
        require(incoming%W[j]==0,
                "nonintegral_original_weighted_orbit_flux")
        action[j]=(72+9*MAG[j])*amplitudes[j]-incoming//W[j]
    return tuple(action),targets,moves


def test():
    validate_source(ADJ)
    psi=tuple(sum(COEFF[k]*BASIS[k][i] for k in range(3))
              for i in range(N))
    support={i for i,v in enumerate(psi) if v}
    require(support=={0,1,2,3},"toy_source_support_not_expected")
    exact=direct_action(psi,ADJ)
    scattered,touched,raw_moves=scatter_action(psi,ADJ)
    require(scattered==exact,"original_H_direct_vs_scatter")
    require(touched==set(range(N)) and len(touched-support)==1,
            "omitted_exterior_K5_like_target")
    require(raw_moves==72*len(support),"raw_source_moves_not_72_per_row")
    g=[[weighted_inner(BASIS[i],BASIS[j])
       for j in range(3)] for i in range(3)]
    require(g==[[1,0,0],[0,5,0],[0,0,6]],
            "expected_weighted_nondiagonal_column_metric")
    k=[[weighted_inner(BASIS[i],direct_action(BASIS[j],ADJ))
       for j in range(3)] for i in range(3)]
    require(all(k[i][j]==k[j][i] for i in range(3) for j in range(3)),
            "weighted_H_not_self_adjoint")
    norm=weighted_inner(psi,psi)
    energy=weighted_inner(psi,exact)
    h2=weighted_inner(exact,exact)
    require(norm==sum(COEFF[i]*g[i][j]*COEFF[j]
              for i in range(3) for j in range(3)),
            "physical_vs_Galerkin_Gram_mismatch")
    require(energy==sum(COEFF[i]*k[i][j]*COEFF[j]
              for i in range(3) for j in range(3)),
            "physical_vs_Galerkin_H_mismatch")
    residual=tuple(D*exact[i]-Z*psi[i] for i in range(N))
    direct_r2=weighted_inner(residual,residual)
    moment_r2=D*D*h2-2*D*Z*energy+Z*Z*norm
    require(direct_r2==moment_r2 and direct_r2>0,
            "physical_residual_moment_identity")
    # b = B^T W (D H-z)psi; G_3^{-1}=diag(1,1/5,1/6).
    b=[weighted_inner(col,residual) for col in BASIS]
    projected30=30*b[0]*b[0]+6*b[1]*b[1]+5*b[2]*b[2]
    exterior30=30*direct_r2-projected30
    require(exterior30>0,"physical_exterior_leakage_not_positive")
    # Direct omission of the K5-like fifth target must not be accepted.
    omitted_r2=sum(W[i]*residual[i]*residual[i] for i in support)
    require(omitted_r2<direct_r2 and
            (direct_r2-omitted_r2)==W[4]*residual[4]*residual[4],
            "exterior_leakage_negative_control_not_rejected")
    stripped,missing,moves=scatter_action(psi,ADJ,skip_exterior=True)
    require(4 not in missing and stripped!=exact,
            "missing_exterior_flux_was_accepted")
    forged=[dict(row) for row in ADJ]
    forged[3][4]=2
    forged[3][3]=68
    try:
        validate_source(tuple(forged))
    except SystemExit:
        forged_rejected=True
    else:
        forged_rejected=False
    require(forged_rejected,"forged_weighted_reverse_accepted")
    # The source-observable action is separately computable in exact W,
    # but this toy does NOT identify or certify an actual physical E2.
    wind_action=tuple(WIND[i]*psi[i] for i in range(N))
    wind_norm=weighted_inner(wind_action,wind_action)
    wind_sample=weighted_inner(psi,wind_action)
    require(wind_norm>0 and wind_sample==sum(
            W[i]*WIND[i]*psi[i]*psi[i] for i in range(N)),
            "observable_physical_weighted_action_mismatch")
    emit("Y137_L_TOY",
         physical_source_rows=len(support),
         original_raw_moves=raw_moves,
         exact_reached_support=len(touched),
         exact_outside_target_count=len(touched-support),
         direct_vs_scattered_H="PASS",
         W_Galerkin_norm_and_H="PASS",
         full_H_residual_moment="EXACT",
         projected_vs_full_residual="POSITIVE_EXTERIOR",
         omitted_exterior_negative_control="REJECTED",
         forged_weighted_edge="REJECTED",
         observable_action_norm_SHA256=digest(wind_norm),
         physical_full_3x4_Ritz_witness="NOT_COMPUTED",
         Wilson_first_spectral_weight="HOLD")
    emit("Y137_L_VERDICT",toy="PASS",
         exact_3x4_physical_source="NEXT_GATE",
         actual_20738_Ritz_witness="NEXT_GATE",
         full_physical_eigenstate_angle="HOLD",
         first_Wilson_weight="HOLD",issue_137="OPEN")


if __name__=="__main__":
    require(sys.argv[1:]==["toy"],"usage_toy_only")
    test()
