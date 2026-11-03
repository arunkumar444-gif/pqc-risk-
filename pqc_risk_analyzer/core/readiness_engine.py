def calculate_pqc_readiness(inv, aw, lib, hyb, test, gov):
    """
    Calculates weighted PQC readiness percentage.
    """
    weighted_sum = (
        (inv * 0.25) +
        (aw * 0.15) +
        (lib * 0.20) +
        (hyb * 0.15) +
        (test * 0.15) +
        (gov * 0.10)
    )
    return round(weighted_sum, 2)