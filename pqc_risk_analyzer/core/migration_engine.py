def generate_recommendation_and_priority(algorithm, purpose, risk_score, lifetime):
    algo_upper = algorithm.upper()
    purpose_upper = purpose.upper()
    
    if "RSA" in algo_upper:
        if "SIGN" in purpose_upper:
            recommended = "FIPS 204 (ML-DSA-65) / FIPS 205 (SLH-DSA)"
            rationale = "RSA digital signatures must transition to Module-Lattice signatures (ML-DSA) or Hash-based signatures (SLH-DSA)."
        else:
            recommended = "FIPS 203 (ML-KEM-768)"
            rationale = "RSA key encapsulation/transport is vulnerable to Shor's algorithm; replace with ML-KEM."
    elif "ECDH" in algo_upper or "DH" in algo_upper:
        recommended = "FIPS 203 (ML-KEM-768)"
        rationale = "Elliptic-curve / Finite-field Diffie-Hellman collapses under Shor's algorithm. Deploy ML-KEM key encapsulation."
    elif "ECDSA" in algo_upper or "ED25519" in algo_upper:
        recommended = "FIPS 204 (ML-DSA-65)"
        rationale = "Elliptic curve digital signatures are vulnerable to Shor's algorithm. Transition to ML-DSA."
    elif "AES-128" in algo_upper:
        recommended = "Migrate to AES-256"
        rationale = "Grover's search reduces AES-128 to 64 bits of security. Upgrade to AES-256 to restore 128-bit quantum security."
    elif "AES-256" in algo_upper:
        recommended = "RETAIN (AES-256)"
        rationale = "AES-256 provides 128-bit post-quantum security against Grover's algorithm."
    elif "ML-KEM" in algo_upper or "ML-DSA" in algo_upper or "SLH-DSA" in algo_upper:
        recommended = "RETAIN (PQC Standard Approved)"
        rationale = "Asset already uses a finalized NIST PQC standard."
    else:
        recommended = "Review Cryptographic Primitive"
        rationale = "Evaluate context and upgrade to appropriate NIST FIPS post-quantum standard."

    # Priority Decision Logic
    if risk_score >= 75.0 or (risk_score >= 60.0 and lifetime >= 4):
        priority = "P1 - High Priority"
    elif risk_score >= 45.0:
        priority = "P2 - Medium Priority"
    else:
        priority = "P3 - Lower Priority"
        
    return recommended, rationale, priority