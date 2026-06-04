def check_columns(cotation, restriction):

    cols_cotation = set(cotation.columns)
    cols_restriction = set(restriction.columns)

    common_cols = cols_cotation & cols_restriction
    only_cotation = cols_cotation - cols_restriction
    only_restriction = cols_restriction - cols_cotation

    print("\n✅ COLONNES COMMUNES (UTILISÉES)")
    print(sorted(common_cols))

    print("\n⚠️ COLONNES UNIQUEMENT DANS COTATION (IGNORÉES)")
    print(sorted(only_cotation))

    print("\n⚠️ COLONNES UNIQUEMENT DANS RESTRICTION (IGNORÉES)")
    print(sorted(only_restriction))

    return {
        "common": common_cols,
        "only_cotation": only_cotation,
        "only_restriction": only_restriction
    }
