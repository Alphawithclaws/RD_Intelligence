import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

MODEL = "claude-sonnet-4-5"

CATEGORIES = [
    "Laptops",
    "Televisions",
    "Air Conditioners",
    "Washing Machines",
    "Mobiles",
]


def load_products(filename):
    with open(
        filename,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_json(text):
    """
    Safely extract the first complete JSON object
    returned by Claude.
    """

    text = text.strip()

    # Remove markdown code fences if Claude added them.
    text = re.sub(
        r"```json",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace("```", "").strip()

    # Find the first JSON object.
    start = text.find("{")

    if start == -1:
        raise ValueError(
            "Claude did not return a JSON object."
        )

    # Find the matching closing brace.
    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):

        char = text[index]

        if char == '"' and not escaped:
            in_string = not in_string

        if char == "\\" and not escaped:
            escaped = True
        else:
            escaped = False

        if not in_string:

            if char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

                if depth == 0:
                    json_text = text[
                        start:index + 1
                    ]

                    return json.loads(json_text)

    raise ValueError(
        "Could not find a complete JSON object "
        "in Claude response."
    )


def normalise_name(name):
    """
    Normalise product names for additional
    validation after Claude matching.
    """

    name = name.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        " ",
        name,
    )

    return name.strip()


def extract_model_tokens(name):
    """
    Extract useful model-number-like tokens.

    Examples:
    15-fb0178ax
    55c655
    65c755
    rm550
    x1 carbon
    """

    name = normalise_name(name)

    tokens = re.findall(
        r"\b[a-z]*\d+[a-z0-9-]*\b",
        name,
    )

    return set(tokens)


def has_strong_model_match(
    reliance_name,
    vijay_name,
):
    """
    Require meaningful evidence that the two products
    are actually the same model.

    Exact model-token overlap is preferred.
    """

    reliance_tokens = extract_model_tokens(
        reliance_name
    )

    vijay_tokens = extract_model_tokens(
        vijay_name
    )

    common_tokens = (
        reliance_tokens
        & vijay_tokens
    )

    if not common_tokens:
        return False

    # Ignore extremely short numeric tokens.
    useful_tokens = [
        token
        for token in common_tokens
        if len(token) >= 4
    ]

    return len(useful_tokens) > 0


def validate_matches(
    result,
    reliance_products,
    vijay_products,
):
    """
    Validate Claude's proposed matches against the
    original scraped datasets.

    This prevents Claude from inventing products
    or matching products with obviously different
    model identifiers.
    """

    reliance_lookup = {
        product["product_name"]:
        product
        for product in reliance_products
    }

    vijay_lookup = {
        product["product_name"]:
        product
        for product in vijay_products
    }

    valid_matches = []

    for match in result.get("matches", []):

        reliance_name = match.get(
            "reliance_product"
        )

        vijay_name = match.get(
            "vijay_sales_product"
        )

        if not reliance_name:
            continue

        if not vijay_name:
            continue

        if reliance_name not in reliance_lookup:
            continue

        if vijay_name not in vijay_lookup:
            continue

        if not match.get(
            "same_product",
            False
        ):
            continue

        # Strong model evidence required.
        if not has_strong_model_match(
            reliance_name,
            vijay_name,
        ):
            continue

        reliance = reliance_lookup[
            reliance_name
        ]

        vijay = vijay_lookup[
            vijay_name
        ]

        reliance_price = reliance.get(
            "price"
        )

        vijay_price = vijay.get(
            "price"
        )

        if reliance_price is None:
            continue

        if vijay_price is None:
            continue

        price_difference = (
            vijay_price
            - reliance_price
        )

        if reliance_price != 0:
            percentage = (
                price_difference
                / reliance_price
            ) * 100
        else:
            percentage = 0

        valid_matches.append(
            {
                "reliance_product":
                    reliance_name,

                "vijay_sales_product":
                    vijay_name,

                "same_product": True,

                "match_reason":
                    match.get(
                        "match_reason",
                        "Matching model information.",
                    ),

                "reliance_price":
                    reliance_price,

                "vijay_sales_price":
                    vijay_price,

                "price_difference":
                    round(
                        price_difference,
                        2,
                    ),

                "price_difference_percent":
                    round(
                        percentage,
                        2,
                    ),
            }
        )

    result["matches"] = valid_matches

    return result


def match_category(
    category,
    reliance_products,
    vijay_products,
):

    prompt = f"""
You are matching products for a retail
competitive intelligence system.

CATEGORY:
{category}

RELIANCE DIGITAL PRODUCTS:
{json.dumps(
    reliance_products,
    indent=2,
    ensure_ascii=False,
)}

VIJAY SALES PRODUCTS:
{json.dumps(
    vijay_products,
    indent=2,
    ensure_ascii=False,
)}

TASK:

Find products that are genuinely the SAME retail
product sold by both retailers.

STRICT MATCHING RULES:

1. The product model must match.

2. Exact model number overlap is the strongest
   evidence.

3. Do NOT match products just because they have
   the same brand.

4. Do NOT match different screen sizes.

5. Do NOT match different RAM configurations.

6. Do NOT match different storage configurations.

7. Do NOT match different processors.

8. Do NOT match different capacities.

9. Do NOT match different generations.

10. Do NOT match products merely because their
    names look similar.

11. If you are uncertain, DO NOT MATCH THEM.

12. Never invent a model number.

13. Only use information present in the supplied
    product data.

IMPORTANT:

For example:

"ASUS Vivobook Go 14"
and
"ASUS Vivobook Go 15"

are NOT automatically the same product.

Likewise:

"HP Victus Ryzen 5"
and
"HP Victus Intel i5"

are NOT automatically the same product.

Only return a match when there is strong evidence
that both retailers are selling the same model.

Return ONLY ONE JSON OBJECT.

Do not write explanations before or after it.

Use exactly this structure:

{{
  "category": "{category}",
  "matches": [
    {{
      "reliance_product": "exact product name",
      "vijay_sales_product": "exact product name",
      "same_product": true,
      "match_reason": "brief evidence for the match"
    }}
  ]
}}

Do NOT calculate prices yourself.

Prices will be calculated by Python after
matching.

If there are no reliable matches, return:

{{
  "category": "{category}",
  "matches": []
}}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=5000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    raw_response = response.content[0].text

    try:
        result = extract_json(
            raw_response
        )

    except Exception as error:

        print()
        print(
            f"Claude JSON error for "
            f"{category}: {error}"
        )

        print()
        print("Raw Claude response:")
        print(raw_response)

        return {
            "category": category,
            "matches": [],
        }

    return validate_matches(
        result,
        reliance_products,
        vijay_products,
    )


def run_matching():

    reliance_file = (
        "data/reliance_products.json"
    )

    vijay_file = (
        "data/vijay_sales_products.json"
    )

    reliance_products = load_products(
        reliance_file
    )

    vijay_products = load_products(
        vijay_file
    )

    all_matches = []

    print()
    print("=" * 70)
    print("PRODUCT MATCHING")
    print("=" * 70)

    for category in CATEGORIES:

        print()
        print(
            f"Matching: {category}"
        )

        reliance_category = [
            product
            for product in reliance_products
            if product.get(
                "category"
            ) == category
        ]

        vijay_category = [
            product
            for product in vijay_products
            if product.get(
                "category"
            ) == category
        ]

        print(
            f"Reliance Digital: "
            f"{len(reliance_category)}"
        )

        print(
            f"Vijay Sales: "
            f"{len(vijay_category)}"
        )

        if not reliance_category:
            print(
                "No Reliance products. Skipping."
            )
            continue

        if not vijay_category:
            print(
                "No Vijay Sales products. Skipping."
            )
            continue

        result = match_category(
            category,
            reliance_category,
            vijay_category,
        )

        matches = result.get(
            "matches",
            [],
        )

        print(
            f"Verified matches: "
            f"{len(matches)}"
        )

        for match in matches:

            print()

            print(
                "  Reliance:"
            )

            print(
                f"  {match['reliance_product']}"
            )

            print(
                "  Vijay Sales:"
            )

            print(
                f"  {match['vijay_sales_product']}"
            )

            print(
                "  Price difference:"
            )

            print(
                f"  ₹{match['price_difference']}"
            )

            print(
                "  Difference %:"
            )

            print(
                f"  {match['price_difference_percent']}%"
            )

        all_matches.append(
            result
        )

    output = {
        "generated_by": "Claude",
        "matching_method":
            "Claude model matching + Python validation",
        "categories": all_matches,
    }

    output_file = (
        "data/product_matches.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    total_matches = sum(
        len(
            category.get(
                "matches",
                [],
            )
        )
        for category in all_matches
    )

    print()
    print("=" * 70)
    print("MATCHING COMPLETE")
    print("=" * 70)

    print(
        f"Total verified matches: "
        f"{total_matches}"
    )

    print(
        f"Saved: {output_file}"
    )


if __name__ == "__main__":
    run_matching()