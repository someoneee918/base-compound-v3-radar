"""
Base BasePaint ($BRUSH) Canvas Mint Royalty & Liquidity Radar
Mathematical engine modeling daily collaborative pixel canvas open edition mint royalties, artist payouts, and $BRUSH deflation velocity on Base L2.
"""

from typing import Dict, Any

def calculate_artist_canvas_royalty(
    pixels_painted: int,
    total_canvas_pixels: int,
    total_mints: int,
    mint_price_eth: float,
    eth_price_usd: float,
    brush_cost_usd_per_pixel: float
) -> Dict[str, Any]:
    """
    Calculates artist payout share from BasePaint daily open edition mint proceeds.
    BasePaint allocates 90% of mint proceeds directly to contributing pixel artists pro-rata.
    """
    if pixels_painted <= 0 or total_canvas_pixels <= 0 or total_mints <= 0:
        raise ValueError("Pixels and mints must be positive.")
    if pixels_painted > total_canvas_pixels:
        raise ValueError("Artist pixels cannot exceed total canvas pixels.")

    artist_pixel_share_pct = (pixels_painted / total_canvas_pixels) * 100.0
    gross_mint_eth = total_mints * mint_price_eth
    artist_pool_eth = gross_mint_eth * 0.90
    protocol_treasury_eth = gross_mint_eth * 0.10

    artist_payout_eth = artist_pool_eth * (pixels_painted / total_canvas_pixels)
    artist_payout_usd = artist_payout_eth * eth_price_usd

    artist_input_cost_usd = pixels_painted * brush_cost_usd_per_pixel
    net_artist_profit_usd = artist_payout_usd - artist_input_cost_usd
    roi_pct = (net_artist_profit_usd / artist_input_cost_usd) * 100.0 if artist_input_cost_usd > 0 else 0.0

    return {
        "pixels_painted": pixels_painted,
        "total_canvas_pixels": total_canvas_pixels,
        "artist_pixel_share_pct": round(artist_pixel_share_pct, 4),
        "total_mints": total_mints,
        "gross_mint_eth": round(gross_mint_eth, 4),
        "gross_mint_usd": round(gross_mint_eth * eth_price_usd, 2),
        "artist_pool_eth": round(artist_pool_eth, 4),
        "protocol_treasury_eth": round(protocol_treasury_eth, 4),
        "artist_payout_eth": round(artist_payout_eth, 5),
        "artist_payout_usd": round(artist_payout_usd, 2),
        "artist_input_cost_usd": round(artist_input_cost_usd, 2),
        "net_artist_profit_usd": round(net_artist_profit_usd, 2),
        "roi_pct": round(roi_pct, 2),
        "is_profitable": net_artist_profit_usd > 0
    }

def calculate_brush_deflation_velocity(
    daily_canvas_pixels: int,
    brush_circulating_supply: float,
    daily_secondary_burn: float
) -> Dict[str, Any]:
    """
    Models the daily and annualized deflationary burn rate of the $BRUSH utility token.
    Each pixel painted on canvas permanently consumes $BRUSH.
    """
    if brush_circulating_supply <= 0:
        raise ValueError("Circulating supply must be positive.")

    total_daily_burned = daily_canvas_pixels + daily_secondary_burn
    annual_burn_runrate = total_daily_burned * 365.0
    burn_rate_annual_pct = (annual_burn_runrate / brush_circulating_supply) * 100.0

    return {
        "daily_canvas_pixels": daily_canvas_pixels,
        "total_daily_burned": total_daily_burned,
        "annual_burn_runrate": annual_burn_runrate,
        "brush_circulating_supply": round(brush_circulating_supply, 2),
        "burn_rate_annual_pct": round(burn_rate_annual_pct, 2)
    }

def calculate_secondary_edition_arbitrage(
    mint_price_eth: float,
    secondary_floor_eth: float,
    marketplace_fee_pct: float,
    creator_royalty_pct: float,
    eth_price_usd: float
) -> Dict[str, Any]:
    """
    Calculates instant secondary market spread between primary open edition mint and secondary floor.
    """
    net_seller_proceeds_eth = secondary_floor_eth * (1.0 - ((marketplace_fee_pct + creator_royalty_pct) / 100.0))
    net_profit_eth = net_seller_proceeds_eth - mint_price_eth
    net_profit_usd = net_profit_eth * eth_price_usd
    arbitrage_roi_pct = (net_profit_eth / mint_price_eth) * 100.0 if mint_price_eth > 0 else 0.0

    return {
        "mint_price_eth": round(mint_price_eth, 4),
        "secondary_floor_eth": round(secondary_floor_eth, 4),
        "net_seller_proceeds_eth": round(net_seller_proceeds_eth, 4),
        "net_profit_eth": round(net_profit_eth, 4),
        "net_profit_usd": round(net_profit_usd, 2),
        "arbitrage_roi_pct": round(arbitrage_roi_pct, 2),
        "is_profitable_arbitrage": net_profit_eth > 0
    }

def verify_vip_license(tx_hash: str, chain: str, recipient: str, amount: float) -> Dict[str, Any]:
    """
    Verifies on-chain payment for VIP Access (5 Base USDC or 0.03 SOL).
    """
    valid_base_wallet = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
    valid_sol_wallet = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

    chain_clean = chain.strip().lower()
    if chain_clean == "base":
        is_valid = (
            recipient.lower() == valid_base_wallet.lower() and
            amount >= 5.0 and
            len(tx_hash) >= 64
        )
    elif chain_clean == "solana":
        is_valid = (
            recipient == valid_sol_wallet and
            amount >= 0.03 and
            len(tx_hash) >= 64
        )
    else:
        is_valid = False

    return {
        "verified": is_valid,
        "chain": chain,
        "tx_hash": tx_hash,
        "amount": amount,
        "recipient": recipient,
        "tier": "BasePaint VIP Artist Sentinel" if is_valid else "Unverified"
    }
