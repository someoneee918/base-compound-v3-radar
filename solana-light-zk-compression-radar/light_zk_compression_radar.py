#!/usr/bin/env python3
"""
Solana Light Protocol ZK Compression State Rent & Validity Proof Radar
Calculates compressed token account rent savings, SVM Groth16 ZK proof verification compute budget,
and batch transaction throughput on Solana.
"""

from typing import Dict, Any


def calculate_zk_state_rent_savings(
    total_token_accounts: int = 1000000,
    traditional_rent_per_account_sol: float = 0.00203928,
    zk_cost_per_leaf_sol: float = 0.000005,
    sol_price_usd: float = 200.0
) -> Dict[str, Any]:
    """
    Computes capital rent savings between traditional SPL Token accounts and
    Light Protocol ZK-compressed token accounts.
    """
    if total_token_accounts <= 0:
        raise ValueError("Total token accounts must be positive")
    if traditional_rent_per_account_sol <= 0.0 or zk_cost_per_leaf_sol < 0.0:
        raise ValueError("Cost values must be positive")

    traditional_total_sol = total_token_accounts * traditional_rent_per_account_sol
    traditional_total_usd = traditional_total_sol * sol_price_usd

    zk_total_sol = total_token_accounts * zk_cost_per_leaf_sol
    zk_total_usd = zk_total_sol * sol_price_usd

    sol_saved = traditional_total_sol - zk_total_sol
    usd_saved = traditional_total_usd - zk_total_usd
    savings_pct = (sol_saved / traditional_total_sol) * 100.0 if traditional_total_sol > 0 else 0.0

    return {
        "total_token_accounts": total_token_accounts,
        "traditional_total_sol": round(traditional_total_sol, 4),
        "traditional_total_usd": round(traditional_total_usd, 2),
        "zk_total_sol": round(zk_total_sol, 4),
        "zk_total_usd": round(zk_total_usd, 2),
        "sol_saved": round(sol_saved, 4),
        "usd_saved": round(usd_saved, 2),
        "savings_pct": round(savings_pct, 4)
    }


def calculate_groth16_compute_budget(
    num_proofs: int = 4,
    units_per_groth16_proof: int = 210000,
    base_tx_overhead_units: int = 15000,
    max_tx_compute_limit: int = 1400000
) -> Dict[str, Any]:
    """
    Calculates SVM Compute Budget Unit (CU) consumption for on-chain Groth16 ZK proof verification
    and determines maximum batch capacity within a single 1.4M CU transaction.
    """
    if num_proofs < 0 or units_per_groth16_proof <= 0:
        raise ValueError("Invalid compute parameters")

    total_proof_cus = num_proofs * units_per_groth16_proof
    total_tx_cus = total_proof_cus + base_tx_overhead_units

    max_possible_proofs = (max_tx_compute_limit - base_tx_overhead_units) // units_per_groth16_proof
    is_within_limit = total_tx_cus <= max_tx_compute_limit
    headroom_cus = max(0, max_tx_compute_limit - total_tx_cus)

    return {
        "num_proofs": num_proofs,
        "units_per_groth16_proof": units_per_groth16_proof,
        "total_tx_cus": total_tx_cus,
        "max_tx_compute_limit": max_tx_compute_limit,
        "max_possible_proofs_per_tx": max_possible_proofs,
        "is_within_limit": is_within_limit,
        "headroom_cus": headroom_cus,
        "cu_utilization_pct": round((total_tx_cus / max_tx_compute_limit) * 100.0, 2)
    }


def calculate_photon_indexer_efficiency(
    monthly_queries: int = 2000000,
    cache_hit_ratio: float = 0.85,
    cost_per_million_queries_usd: float = 15.0
) -> Dict[str, Any]:
    """
    Calculates RPC credit and infrastructure cost savings when using Photon indexers
    with client-side state proof caching.
    """
    if monthly_queries <= 0 or not (0.0 <= cache_hit_ratio <= 1.0):
        raise ValueError("Invalid indexer parameters")

    uncached_queries = monthly_queries
    actual_rpc_queries = int(monthly_queries * (1.0 - cache_hit_ratio))

    uncached_cost_usd = (uncached_queries / 1000000.0) * cost_per_million_queries_usd
    actual_cost_usd = (actual_rpc_queries / 1000000.0) * cost_per_million_queries_usd
    usd_saved = uncached_cost_usd - actual_cost_usd
    savings_pct = cache_hit_ratio * 100.0

    return {
        "monthly_queries": monthly_queries,
        "cache_hit_ratio": cache_hit_ratio,
        "actual_rpc_queries": actual_rpc_queries,
        "uncached_cost_usd": round(uncached_cost_usd, 2),
        "actual_cost_usd": round(actual_cost_usd, 2),
        "usd_saved": round(usd_saved, 2),
        "savings_pct": round(savings_pct, 2)
    }


def evaluate_zk_architecture_viability(
    total_accounts: int,
    tx_throughput_per_sec: float
) -> Dict[str, Any]:
    """
    Evaluates enterprise architectural suitability for migrating to ZK Compression on Solana.
    """
    if total_accounts <= 0:
        raise ValueError("Total accounts must be positive")

    if total_accounts >= 100000:
        recommendation = "MANDATORY_ZK_COMPRESSION"
        rationale = "Large-scale distribution. Traditional rent exceeds $40k; ZK compression slashes costs to under $100."
    elif total_accounts >= 10000:
        recommendation = "HIGHLY_BENEFICIAL"
        rationale = "Mid-scale userbase. Compressing token accounts yields >99% rent savings with modest ZK proving overhead."
    else:
        recommendation = "OPTIONAL_EVALUATION"
        rationale = "Small account volume. Standard SPL token accounts may be sufficient if transaction batching is not required."

    return {
        "total_accounts": total_accounts,
        "tx_throughput_per_sec": tx_throughput_per_sec,
        "recommendation": recommendation,
        "rationale": rationale
    }


if __name__ == "__main__":
    rent_res = calculate_zk_state_rent_savings()
    print("State Rent Savings:", rent_res)
    cu_res = calculate_groth16_compute_budget()
    print("Groth16 Compute Budget:", cu_res)
    idx_res = calculate_photon_indexer_efficiency()
    print("Photon Efficiency:", idx_res)
    via = evaluate_zk_architecture_viability(1000000, 50.0)
    print("Viability:", via)
