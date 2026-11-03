def calculate_quantum_risk(c, s, l, e, b):
    """
    Formula: R = 100 * (0.35*C + 0.20*S + 0.20*L + 0.15*E + 0.10*B) / 5
    """
    raw_score = (0.35 * c) + (0.20 * s) + (0.20 * l) + (0.15 * e) + (0.10 * b)
    overall_score = round(100 * (raw_score / 5.0), 2)
    
    if overall_score >= 75.0:
        category = "CRITICAL"
    elif overall_score >= 55.0:
        category = "HIGH"
    elif overall_score >= 35.0:
        category = "MEDIUM"
    else:
        category = "LOW"
        
    return overall_score, category