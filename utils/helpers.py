def get_signal_strength(result):
    """
    Dummy function to assign signal confidence based on signal type.
    Can be enhanced using real price action & technical analysis.
    """
    base_score = {
        'bullish': 85,
        'bearish': 80,
        'sideways': 70
    }

    # Add custom weight based on symbol or timeframe if needed
    signal = result.get('signal', 'sideways').lower()
    return base_score.get(signal, 70)
