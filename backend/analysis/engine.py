def generate_earnings_summary(ticker: str, earnings_list: list[dict]) -> str:
    beaten_earnings = [e for e in earnings_list if e.get("surprise_pct", 0) > 0]
    avg_surprise = round(sum(e["surprise_pct"] for e in beaten_earnings) / len(beaten_earnings), 2) if beaten_earnings else 0
    avg_move = round(sum(abs(e.get("price_ref_close", 0) - e.get("price_ref_open", 0)) / e.get("price_ref_open") * 100 for e in earnings_list) / len(earnings_list), 2) if earnings_list else 0

    price_increases = [e for e in earnings_list if e.get("price_ref_open", 0) > e.get("price_ref_close", 0)]
    price_decreases = [e for e in earnings_list if e.get("price_ref_open", 0) < e.get("price_ref_close", 0)]
    
    num_beats = len(beaten_earnings)
    num_up = len(price_increases)
    num_down = len(price_decreases)

    # High Beat + High Price Success
    if num_beats >= 4 and num_up >= 4:
        summary = (
            f"{ticker} consistently delivers post-earnings upside, reliably clearing both analyst estimates and "
            "options market expectations. This presents a strong setup for directional bullish plays "
            "(e.g., long calls or bull call spreads), provided the historical price gap consistently "
            "exceeds the at-the-money implied move."
        )

    # High Beat + Low Price Success
    elif num_beats >= 4 and num_down >= 3:
        summary = (
            "Despite consistent earnings beats, the stock routinely sells off, indicating severe "
            "'priced to perfection' conditions. This behavior favors contrarian bearish strategies "
            "(e.g., long puts) or premium-selling strategies to capitalize on the heavy "
            "post-earnings IV crush."
        )

    # Consistent Beats + Mixed Price Action
    elif num_beats >= 4 and num_up >= 2 and num_down >= 2:
        summary = (
            f"{ticker} reliably beats earnings estimates but has an unpredictable price reaction, often "
            "influenced by forward guidance or macro factors. This creates a complex environment "
            "where both bullish and bearish strategies can be viable, depending on the broader market "
            "context and specific earnings catalysts."
        )

    # High Surprise + Mixed Price Action
    elif avg_surprise > 15:
        summary = (
            f"{ticker} is highly explosive around earnings, averaging massive {avg_surprise}% financial "
            "surprises. While directional predictability is low, the sheer magnitude of the "
            "post-earnings gap often overpowers options premium costs. This is a prime candidate for "
            "vega-long, direction-neutral strategies like long straddles or strangles."
        )

    # Low Beats + Recent Price Strength
    elif num_beats <= 2 and num_up >= 3:
        summary = (
            f"{ticker} exhibits a 'bad news is good news' asymmetry. It routinely misses estimates, yet "
            "the stock surges-often driven by short squeezes or forward guidance overshadowing past "
            "performance. Buying downside puts here is historically a losing trade; consider bullish "
            "contrarian setups or ratio spreads to capture the upside."
        )

    # Low Beats + Consistent Price Drops
    elif num_beats <= 2 and num_down >= 4:
        summary = (
            f"{ticker} routinely fails to meet expectations and suffers "
            "significant price gaps down. For options traders, this steady fundamental decay offers "
            "high-probability setups for directional bearish plays, such as long puts or bear put "
            "spreads, capitalizing on reliable sell-offs."
        )

    # Moderate Beats + High Price Drops
    elif num_beats >= 3 and num_down >= 4:
        summary = (
            f"{ticker} suffers from inflated 'whisper' numbers. It often beats official estimates but "
            "still gaps down, heavily punishing bullish premium buyers. This dynamic is lucrative for "
            "volatility sellers (e.g., iron condors, short strangles) aiming to capture the IV crush, "
            "or targeted bearish debit spreads."
        )

    # Frequent misses, consistent price drops
    elif num_beats <= 2 and num_down >= 4:
        summary = (
            f"{ticker} consistently misses estimates and experiences significant price declines. This "
            "pattern indicates a persistent fundamental issue, making it a candidate for directional "
            "bearish strategies."
        )

    # 8. Macro-Driven / Premium Seller's Market
    else:
        summary = (
            f"{ticker} shows noisy, inconclusive reactions to earnings with no reliable directional "
            "edge. Because the stock rarely breaks out of its expected move based purely on earnings, "
            "buying options premium here is historically disadvantageous. This environment favors "
            "delta-neutral premium selling or avoiding the event entirely."
        )
    
    # Add a final note on the average price move relative to the implied move
    if avg_move < 2:
        summary += (
            f" The average post-earnings price move is modest ({avg_move}%), often failing to exceed "
            "the at-the-money implied move. This further diminishes the attractiveness of long premium "
            "strategies, as the risk of a breakeven gap is high."
        )
    elif avg_move > 5:
        summary += (
            f" The average post-earnings price move is substantial ({avg_move}%), frequently surpassing "
            "the at-the-money implied move. This enhances the potential profitability of long premium "
            "strategies, as the likelihood of a significant gap increases. However, the unpredictability "
            "of the direction still warrants caution and favors strategies that can capitalize on "
            "volatility rather than directional bets."
        )
        
    # Look at price actions for last 2 earnings for recent trend
    if len(earnings_list) >= 2:
        last_2 = earnings_list[-2:]
        last_2_up = sum(1 for e in last_2 if e.get("price_ref_open", 0) > e.get("price_ref_close", 0))
        last_2_down = sum(1 for e in last_2 if e.get("price_ref_open", 0) < e.get("price_ref_close", 0))
        if last_2_up == 2:
            summary += "\nNotably, the last two quarterly earnings have both resulted in price increases, suggesting a potential short-term bullish trend."
        elif last_2_down == 2:
            summary += "\nNotably, the last two quarterly earnings have both resulted in price decreases, suggesting a potential short-term bearish trend."
    
    return summary
    
def compute_impact_factors(earnings_list: list[dict]) -> None:
    for earnings in earnings_list:
        price_open = earnings.get("price_ref_open")
        price_close = earnings.get("price_ref_close")
        sector_open = earnings.get("sector_ref_open")
        sector_close = earnings.get("sector_ref_close")
        vix_val = earnings.get("vix_val")

        if None in [price_open, price_close, sector_open, sector_close]:
            continue

        price_change_pct = round((price_open - price_close) / price_close * 100, 2)
        sector_change_pct = round((sector_open - sector_close) / sector_close * 100, 2)
        
        # Calculate the Idiosyncratic Signal (Excess Return)
        excess_return = abs(price_change_pct - sector_change_pct)
        
        # Calculate Earnings Attribution Score
        vix_safe = vix_val if (vix_val) else 20
        
        attribution_score = compute_attribution(price_change_pct, sector_change_pct, vix_safe)
        
        volatility_factor = "neutral"
        if vix_val:
            if vix_val > 30:
                volatility_factor = "high"
            elif vix_val < 15:
                volatility_factor = "low"

        sector_influence = "strong" if abs(sector_change_pct) > 1.5 else "weak"

        # Determine Primary Driver
        if volatility_factor == "high":
            primary_driver = "Market Noise"
        elif excess_return > abs(sector_change_pct) and excess_return > 2.0:
            primary_driver = "Earnings/Idiosyncratic"
        elif sector_influence == "strong":
            primary_driver = "Sector Trend"
        else:
            primary_driver = "Indeterminate"

        summary = {
            "excess_return": round(excess_return, 2),
            "earnings_attribution_score": attribution_score,
            "volatility_factor": volatility_factor,
            "sector_influence": sector_influence,
            "primary_driver": primary_driver
        }
        earnings["impact_factors"] = summary
        
def compute_attribution(price_change_pct: float, sector_return: float, vix_val: float) -> int:
    excess_return = price_change_pct - sector_return

    # What fraction of the total absolute move is earnings-driven
    total_abs = abs(excess_return) + abs(sector_return)
    if total_abs == 0:
        return {"attribution_score": 0.0}

    raw_earnings_share = abs(excess_return / total_abs)  # can be negative if earnings hurt

    # VIX confidence: high VIX means sector itself is noisy, so we're less confident the excess move is truly earnings-driven
    if vix_val < 15:
        vix_confidence = 1.00
    elif vix_val < 22:
        vix_confidence = 0.95
    elif vix_val < 30:
        vix_confidence = 0.8
    else:
        vix_confidence = 0.6

    attribution_score = round(raw_earnings_share * vix_confidence, 2)
    return attribution_score