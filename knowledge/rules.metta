(yield x) (gt x 100) -> (flag suspicious_yield weight 40 why "APR>100").
(contract_age d) (lt d 7) -> (flag young_contract weight 30 why "age<7d").
(protocol p) (is_unverified p) -> (flag unverified_protocol weight 20 why "no registry").
(score S) :- sum(flags.weights) -> S.
