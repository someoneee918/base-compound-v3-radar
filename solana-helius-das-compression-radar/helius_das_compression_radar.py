#!/usr/bin/env python3
"""
Solana Helius RPC & DAS (Digital Asset Standard) State Compression Read-Cost Optimization Radar
Calculates DAS batch query credit efficiency, Concurrent Merkle Tree canopy proof size reduction,
and on-chain rent capital savings for compressed assets (cNFTs / ZK compression).
"""

from typing import Dict, Any


def calculate_das_rpc_batch_savings(
    total_assets_queried: int = 500000,
    single_query_credits: int = 10,
    batch_size: int = 100,
    batch_query_credits: int = 50,
    cost_per_million_credits_usd: float = 10.0
) -> Dict[str, Any]:
    """
    Computes RPC credit consumption and dollar cost between individual getAsset
    calls vs optimized getAssetBatch / getAssetsByOwner DAS queries.
    """
    if total_assets_queried <= 0 or batch_size <= 0:
        raise ValueError("Assets queried and batch size must be positive")

    unbatched_credits = total_assets_queried * single_query_credits
    num_batches = (total_assets_queried + batch_size - 1) // batch_size
    batched_credits = num_batches * batch_query_credits

    credits_saved = unbatched_credits - batched_credits
    credit_savings_pct = (credits_saved / unbatched_credits) * 100.0 if unbatched_credits > 0 else 0.0

    unbatched_cost_usd = (unbatched_credits / 1_000_000.0) * cost_per_million_credits_usd
    batched_cost_usd = (batched_credits / 1_000_000.0) * cost_per_million_credits_usd
    usd_saved = unbatched_cost_usd - batched_cost_usd

    return {
        "total_assets_queried": total_assets_queried,
        "batch_size": batch_size,
        "num_batches": num_batches,
        "unbatched_credits": unbatched_credits,
        "batched_credits": batched_credits,
        "credits_saved": credits_saved,
        "credit_savings_pct": round(credit_savings_pct, 2),
        "unbatched_cost_usd": round(unbatched_cost_usd, 2),
        "batched_cost_usd": round(batched_cost_usd, 2),
        "usd_saved": round(usd_saved, 2)
    }


def calculate_canopy_proof_overhead(
    max_depth: int = 20,
    canopy_depth: int = 10,
    hash_size_bytes: int = 32
) -> Dict[str, Any]:
    """
    Calculates transaction packet overhead reduction via Concurrent Merkle Tree canopy depth.
    Canopy stores top C levels on-chain, omitting them from the client-submitted proof.
    """
    if max_depth <= 0:
        raise ValueError("max_depth must be positive")
    if canopy_depth < 0 or canopy_depth > max_depth:
        raise ValueError("canopy_depth must be between 0 and max_depth")

    full_proof_length = max_depth
    transmitted_proof_length = max_depth - canopy_depth
    full_proof_bytes = full_proof_length * hash_size_bytes
    transmitted_proof_bytes = transmitted_proof_length * hash_size_bytes
    bytes_saved = canopy_depth * hash_size_bytes
    overhead_reduction_pct = (canopy_depth / max_depth) * 100.0

    return {
        "max_depth": max_depth,
        "canopy_depth": canopy_depth,
        "full_proof_hashes": full_proof_length,
        "transmitted_proof_hashes": transmitted_proof_length,
        "full_proof_bytes": full_proof_bytes,
        "transmitted_proof_bytes": transmitted_proof_bytes,
        "bytes_saved_per_tx": bytes_saved,
        "overhead_reduction_pct": round(overhead_reduction_pct, 2)
    }


def calculate_concurrent_merkle_tree_rent_savings(
    total_mint_capacity: int = 1000000,
    max_depth: int = 20,
    max_buffer_size: int = 64,
    canopy_depth: int = 14,
    sol_price_usd: float = 200.0
) -> Dict[str, Any]:
    """
    Compares traditional SPL Token/NFT account rent against Concurrent Merkle Tree creation rent.
    Standard Solana account rent is 0.00203928 SOL per mint/token account.
    A depth 20 tree stores up to 2^20 (1,048,576) items.
    """
    if total_mint_capacity <= 0:
        raise ValueError("total_mint_capacity must be positive")

    traditional_rent_per_account_sol = 0.00203928
    traditional_total_rent_sol = total_mint_capacity * traditional_rent_per_account_sol
    traditional_total_cost_usd = traditional_total_rent_sol * sol_price_usd

    # Base tree size + canopy size rent model (SPL Account Compression)
    # 2^canopy_depth nodes cached on-chain + changelog buffer
    canopy_nodes = (1 << (canopy_depth + 1)) - 2 if canopy_depth > 0 else 0
    tree_rent_sol = 1.25 + (canopy_nodes * 0.00028) + (max_buffer_size * 0.005)
    # Clamping standard realistic tree rent (depth 20, canopy 14 ~ 10.15 SOL)
    tree_rent_sol = min(tree_rent_sol, 10.15) if canopy_depth <= 14 else tree_rent_sol
    tree_cost_usd = tree_rent_sol * sol_price_usd

    rent_saved_sol = traditional_total_rent_sol - tree_rent_sol
    usd_saved = traditional_total_cost_usd - tree_cost_usd
    savings_pct = (rent_saved_sol / traditional_total_rent_sol) * 100.0 if traditional_total_rent_sol > 0 else 0.0

    return {
        "total_mint_capacity": total_mint_capacity,
        "max_depth": max_depth,
        "max_buffer_size": max_buffer_size,
        "canopy_depth": canopy_depth,
        "traditional_total_rent_sol": round(traditional_total_rent_sol, 4),
        "traditional_total_cost_usd": round(traditional_total_cost_usd, 2),
        "tree_rent_sol": round(tree_rent_sol, 4),
        "tree_cost_usd": round(tree_cost_usd, 2),
        "rent_saved_sol": round(rent_saved_sol, 4),
        "usd_saved": round(usd_saved, 2),
        "savings_pct": round(savings_pct, 2)
    }


def evaluate_das_indexing_health(
    monthly_queries: int = 1000000,
    batch_ratio: float = 0.90,
    canopy_depth: int = 12,
    max_depth: int = 20
) -> Dict[str, Any]:
    """
    Evaluates DAS architecture efficiency score (0-100) and gives actionable recommendations.
    """
    if monthly_queries < 0 or not (0.0 <= batch_ratio <= 1.0):
        raise ValueError("Invalid parameters for indexing health evaluation")

    batch_score = batch_ratio * 60.0  # Up to 60 points for batching
    canopy_ratio = canopy_depth / max_depth if max_depth > 0 else 0.0
    canopy_score = min(canopy_ratio, 1.0) * 40.0  # Up to 40 points for canopy optimization

    health_score = round(batch_score + canopy_score, 1)

    if health_score >= 80.0:
        status = "HIGHLY_OPTIMIZED"
        recommendation = "Optimal DAS indexing. Minimal RPC credits burned and low tx packet overhead."
    elif health_score >= 50.0:
        status = "MODERATE_EFFICIENCY"
        recommendation = "Increase batch size in getAssetBatch queries to reduce redundant RPC credits."
    else:
        status = "UNOPTIMIZED_CREDIT_LEAK"
        recommendation = "Severe RPC credit waste. Migrate single getAsset queries to batch DAS API immediately."

    return {
        "monthly_queries": monthly_queries,
        "batch_ratio": batch_ratio,
        "canopy_depth": canopy_depth,
        "health_score": health_score,
        "status": status,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    batch_res = calculate_das_rpc_batch_savings()
    print("DAS Batch Savings:", batch_res)
    canopy_res = calculate_canopy_proof_overhead()
    print("Canopy Overhead:", canopy_res)
    rent_res = calculate_concurrent_merkle_tree_rent_savings()
    print("Rent Savings:", rent_res)
    health = evaluate_das_indexing_health()
    print("Indexing Health:", health)
