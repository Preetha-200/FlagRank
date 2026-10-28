# Observable Signal Specification & Feature Roles

## 1. Role Definitions
- **EXPLANATORY SIGNAL**: Observable product/marketplace characteristic used to estimate expected ranking.
- **RANKING CONTEXT / CONTROL**: Variable defining the competition scope; needed for fair comparison but not a direct product-quality signal.
- **OBSERVED OUTCOME**: The actual ranking the framework is trying to explain.
- **SECONDARY / VALIDATION ONLY**: Derived variable used to validate results, never to predict observed ranking.
- **EXCLUDE**: Empty, constant, or uniquely identifying variables, or those risking methodological circularity.

## 2. Signal Specification Table

| Column | Meaning | Research Role | Use in Expected-Ranking Model? | Leakage/Circularity Risk | Reason |
|--------|---------|---------------|--------------------------------|--------------------------|--------|
| `amazon_rank` | The actual rank of the product | **OBSERVED OUTCOME** | No | Extreme | This is the outcome we are estimating. |
| `is_amazon_top6` | Boolean if rank is 1-6 | **SECONDARY / VALIDATION ONLY** | No | Extreme | Directly derived from the observed outcome. |
| `query` | The user search term | **RANKING CONTEXT** | Context Only | Low | Defines the competitive peer group. |
| `category` | The Amazon category | **RANKING CONTEXT** | Context Only | Low | Defines the competitive peer group. |
| `title` | Product title | **EXPLANATORY SIGNAL** | Yes | Low | Text relevance strongly drives organic rank. |
| `description` | Product description | **EXPLANATORY SIGNAL** | Yes | Low | Text relevance strongly drives organic rank. |
| `brand` | Product brand | **EXPLANATORY SIGNAL** | Yes | Low | Brand authority is a legitimate ranking factor. |
| `product_type` | Specific product categorization | **EXPLANATORY SIGNAL** | Yes | Low | Aids in semantic relevance matching. |
| `price` | Current selling price | **EXPLANATORY SIGNAL** | Yes | Low | Pricing strategy affects expected visibility. |
| `original_price` | Original listing price | **EXPLANATORY SIGNAL** | Yes | Low | Indicates perceived value/premium status. |
| `discounted` | Whether product is on sale | **EXPLANATORY SIGNAL** | Yes | Low | Promotions temporarily boost expected ranking. |
| `savings_percent` | Discount depth | **EXPLANATORY SIGNAL** | Yes | Low | Correlated with click-through incentives. |
| `rating` | Average star rating | **EXPLANATORY SIGNAL** | Yes | Low | Core observable quality metric. |
| `total_reviews` | Volume of reviews | **EXPLANATORY SIGNAL** | Yes | Low | Core observable popularity metric. |
| `sponsored` | Paid advertising placement | **EXPLANATORY SIGNAL** | Yes | High | While platform-generated, it legally explains sudden rank jumps. If excluded, paid products will falsely flag as "suspiciously ranked". |
| `color` | Product variant color | **EXPLANATORY SIGNAL** | Yes | Low | Though sparse, it might marginally impact click-through. |
| `asin` | Amazon Standard Id. Number | **EXCLUDE** | No | None | Unique identifier; memorizing it causes overfitting. |
| `url` | Product URL | **EXCLUDE** | No | None | Unique text identifier. |
| `thumbnail` | Image URL | **EXCLUDE** | No | None | Image hash/URL offers no tabular predictive value. |
| `currency` | Currency code | **EXCLUDE** | No | None | Constant across the dataset or uninformative. |

*(Note: `amazon_choice`, `best_seller`, `amazon_prime`, and `features_raw` were excluded during preprocessing due to zero variance or 100% missing values).*

## 3. Investigating Potential Circularity (`sponsored`)
- **Observation:** `sponsored` flags whether a seller paid for placement.
- **Risk:** It is platform-injected visibility rather than an organic marketplace signal (like a customer review).
- **Recommendation:** It **must** be included as an EXPLANATORY SIGNAL. If the framework attempts to estimate expected rank strictly from organic signals (price, reviews) while ignoring paid placements, all `sponsored` products will severely deviate from their expected organic rank and be flagged as "Suspicious." Since paying for ads is a *legitimate, explainable* reason for a high rank, the model must account for it to isolate *unexplained* manipulations (e.g., brushing attacks).

## 4. Context vs Signals (`query` and `category`)
- **Analysis:** A rank of `5` is meaningless without knowing the `query` it was ranked for. A product ranked `5` for "laptop" faces entirely different competition than a product ranked `5` for "blue mechanical keyboard switch".
- **Recommendation:** `query` and `category` must be treated as **RANKING CONTEXT / CONTROL**. They should not be directly fed into a regression model as dummy variables. Instead, they dictate the boundaries for query-level expected-ranking models and peer-group analysis.
