"""
Machine-readable feature schema mapping engineered features to their origins and transformations.
"""

FEATURE_SCHEMA = [
    {
        "feature_name": "feat_price",
        "source_column": "price",
        "signal_type": "numeric",
        "transformation": "pass-through (float)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_original_price",
        "source_column": "original_price",
        "signal_type": "numeric",
        "transformation": "pass-through (float)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_savings_percent",
        "source_column": "savings_percent",
        "signal_type": "numeric",
        "transformation": "pass-through (float)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_rating",
        "source_column": "rating",
        "signal_type": "numeric",
        "transformation": "pass-through (float)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_total_reviews_log",
        "source_column": "total_reviews",
        "signal_type": "numeric",
        "transformation": "log1p (log(x+1)) due to heavy right skew",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_discounted",
        "source_column": "discounted",
        "signal_type": "boolean",
        "transformation": "cast to int (0/1)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_sponsored",
        "source_column": "sponsored",
        "signal_type": "boolean",
        "transformation": "cast to int (0/1)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_brand_freq",
        "source_column": "brand",
        "signal_type": "categorical",
        "transformation": "frequency encoding (normalized value counts)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_product_type_freq",
        "source_column": "product_type",
        "signal_type": "categorical",
        "transformation": "frequency encoding (normalized value counts)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_color_freq",
        "source_column": "color",
        "signal_type": "categorical",
        "transformation": "frequency encoding (normalized value counts)",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_title_length",
        "source_column": "title",
        "signal_type": "text",
        "transformation": "string length character count",
        "eligible_for_expected_ranking": True
    },
    {
        "feature_name": "feat_title_query_overlap",
        "source_column": "title, query",
        "signal_type": "text",
        "transformation": "ratio of query unigrams present in title",
        "eligible_for_expected_ranking": True
    }
]
