"""
rag_query.py
-------------
Single-file interactive tester for the SabiLens NAFDAC RAG system.

Loads the vector store and runs queries directly from the command line —
no API server needed.  Useful for quickly verifying that ingestion worked
and that retrieval + scoring behave correctly before demoing.

USAGE
─────
  # Interactive menu (default):
  python rag_query.py

  # Verify a specific product directly:
  python rag_query.py --nafdac "A8-4114" --category "corn flakes"

  # Semantic search by product text:
  python rag_query.py --search "kelloggs cereal nigeria"

  # Browse all products in a subcategory:
  python rag_query.py --browse "Cosmetics"

  # Run all built-in demo scenarios automatically:
  python rag_query.py --demo

PRE-REQUISITES
──────────────
  1. pip install -r requirements.txt
  2. python main.py --mode ingest    ← must be run at least once first

The script must be run from the project root (the folder that contains
main.py, data/, chroma_db/, etc.).
"""

import sys
import os
import argparse
import textwrap

# ── Ensure project root is on the path ───────────────────────────────────────
# This allows `python rag_query.py` to be called from anywhere inside the
# project without needing to install the package.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Colour helpers (works on macOS, Linux, and Windows 10+) ──────────────────

class C:
    """ANSI colour codes for terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"

def _coloured(text: str, colour: str) -> str:
    """Wrap text in an ANSI colour code if stdout is a terminal."""
    if sys.stdout.isatty():
        return f"{colour}{text}{C.RESET}"
    return text

def green(t):  return _coloured(t, C.GREEN)
def yellow(t): return _coloured(t, C.YELLOW)
def red(t):    return _coloured(t, C.RED)
def cyan(t):   return _coloured(t, C.CYAN)
def bold(t):   return _coloured(t, C.BOLD)
def dim(t):    return _coloured(t, C.DIM)


# ── Score → display helpers ───────────────────────────────────────────────────

_STATUS_ICONS = {
    "VERIFIED"              : green("✅  VERIFIED"),
    "VERIFIED_NEAR_EXPIRY"  : yellow("⚠️   VERIFIED (near expiry)"),
    "SUBCATEGORY_MISMATCH"  : red("🚨  SUBCATEGORY MISMATCH"),
    "EXPIRED"               : red("❌  EXPIRED"),
    "NOT_FOUND"             : red("❌  NOT FOUND"),
}

_SEVERITY_COLOURS = {
    "NONE"     : green,
    "WARNING"  : yellow,
    "HIGH"     : red,
    "CRITICAL" : red,
}

def _score_bar(score: float, width: int = 30) -> str:
    """Render a simple ASCII score bar, e.g.  [██████████░░░░░░░░░░░░]  0.33"""
    filled = round(score * width)
    bar    = "█" * filled + "░" * (width - filled)
    colour = green if score >= 0.85 else (yellow if score >= 0.5 else red)
    return colour(f"[{bar}]") + f"  {score:.2f}"


# ── Pretty-printers ───────────────────────────────────────────────────────────

def _print_divider(char: str = "─", width: int = 65):
    print(dim(char * width))

def _print_header(title: str):
    _print_divider("═")
    print(bold(f"  {title}"))
    _print_divider("═")

def _print_verify_result(result: dict, nafdac_input: str, scanned_cat: str):
    """Print a full verification result in a clean, readable layout."""
    status_icon = _STATUS_ICONS.get(result["status_code"], result["status_code"])
    sev_colour  = _SEVERITY_COLOURS.get(result["severity"], str)

    print()
    _print_divider()
    print(f"  {bold('NAFDAC Number  :')} {cyan(nafdac_input)}")
    print(f"  {bold('Scanned As     :')} {scanned_cat}")
    print(f"  {bold('Status         :')} {status_icon}")
    print(f"  {bold('Score          :')} {_score_bar(result['verification_score'])}")
    print(f"  {bold('Severity       :')} {sev_colour(result['severity'])}")
    _print_divider()

    # Matched record details
    rec = result.get("matched_record")
    if rec:
        print(f"  {bold('Product        :')} {rec.get('product_name', '—')}")
        print(f"  {bold('Registered As  :')} {rec.get('subcategory', '—')}")
        print(f"  {bold('Applicant      :')} {rec.get('applicant_name', '—')}")
        print(f"  {bold('Manufacturer   :')} {rec.get('manufacturer', '—')}")
        print(f"  {bold('Expiry Date    :')} {rec.get('expiry_date_iso', '—')}")
        print(f"  {bold('Presentation   :')} {rec.get('presentation', '—')}")
        _print_divider()

    # Expiry check detail
    expiry = result.get("expiry_check")
    if expiry:
        exp_colour = yellow if expiry.get("is_near_expiry") else (
                     red    if not expiry.get("is_valid")   else green)
        print(f"  {bold('Expiry Check   :')} {exp_colour(expiry['message'])}")

    # Alignment detail
    align = result.get("alignment")
    if align:
        al_colour = green if align["is_match"] else red
        label = "✓ Match" if align["is_match"] else "✗ Mismatch"
        print(f"  {bold('Category Check :')} {al_colour(label)}")
        print(f"    Scanned     → {align['scanned_norm']}")
        print(f"    Registered  → {align['registered_norm']}")

    _print_divider()

    # Full explanation (wrapped at 60 chars)
    print(f"\n  {bold('Detail:')}")
    wrapped = textwrap.fill(result.get("detail", ""), width=60,
                            initial_indent="    ", subsequent_indent="    ")
    print(wrapped)
    print()


def _print_search_results(results: list, query: str):
    """Print semantic search results."""
    print()
    _print_divider()
    print(f"  {bold('Search Query   :')} {cyan(query)}")
    print(f"  {bold('Results Found  :')} {len(results)}")
    _print_divider()

    if not results:
        print(yellow("  No results above the similarity threshold (0.68)."))
        print(dim("  Try a different query or lower SIMILARITY_THRESHOLD in config/settings.py"))
        print()
        return

    for i, r in enumerate(results, 1):
        meta  = r.get("metadata", {})
        score = r.get("similarity_score", 0)
        score_colour = green if score >= 0.85 else (yellow if score >= 0.70 else dim)
        print(f"  {bold(f'#{i}')}  {score_colour(f'sim={score:.4f}')}  "
              f"{meta.get('product_name', '—')}")
        print(f"      NAFDAC: {cyan(meta.get('nafdac_no_clean', '—'))}"
              f"  │  Category: {meta.get('subcategory', '—')}")
        print(f"      Expiry: {meta.get('expiry_date_iso', '—')}"
              f"  │  Applicant: {meta.get('applicant_name', '—')}")
        if i < len(results):
            print(dim("      ·  ·  ·"))
    print()


def _print_category_results(records: list, subcategory: str):
    """Print all products in a subcategory."""
    print()
    _print_divider()
    print(f"  {bold('Category       :')} {cyan(subcategory)}")
    print(f"  {bold('Products Found :')} {len(records)}")
    _print_divider()

    if not records:
        print(yellow(f"  No products found for '{subcategory}'."))
        print(dim("  Valid categories: Cereals and Cereal Products | Cosmetics |"))
        print(dim("  Fats and oils, and Fat Emulsions | Salts, Spices, Soups,"))
        print(dim("  Sauces, Salads and Seasoning | Beverages | Sweeteners"))
        print()
        return

    for rec in records:
        print(f"  {bold('•')} {rec.get('product_name', '—')}")
        print(f"      NAFDAC: {cyan(rec.get('nafdac_no_clean', '—'))}"
              f"  │  Expiry: {rec.get('expiry_date_iso', '—')}")
        print(f"      Applicant: {rec.get('applicant_name', '—')}")
    print()


# ── Core query functions (wraps the real pipeline modules) ────────────────────

def verify_product(retriever, nafdac_no: str, scanned_category: str):
    """Run full four-layer verification and print the result."""
    from retrieval.regulatory_scorer import compute_verification_score
    records = retriever.retrieve_by_nafdac_no(nafdac_no)
    result  = compute_verification_score(nafdac_no, scanned_category, records)
    _print_verify_result(result, nafdac_no, scanned_category)
    return result


def search_products(retriever, query: str, n: int = 5):
    """Run semantic text search and print ranked results."""
    results = retriever.retrieve_by_product_text(query, n=n)
    _print_search_results(results, query)
    return results


def browse_category(retriever, subcategory: str):
    """List all products in a subcategory."""
    records = retriever.retrieve_by_subcategory(subcategory, n=20)
    _print_category_results(records, subcategory)
    return records


# ── Built-in demo scenarios ───────────────────────────────────────────────────

DEMO_SCENARIOS = [
    # (label, nafdac, scanned_category, expected_status)
    ("Authentic — Kellogg's Corn Flakes",
     "A8-4114",    "corn flakes",       "VERIFIED"),

    ("Authentic — Indomie Noodles",
     "01-0877",    "noodles",           "VERIFIED"),

    ("Authentic — Vaseline Petroleum Jelly",
     "02-0385",    "petroleum jelly",   "VERIFIED"),

    ("Authentic — Dangote Sugar",
     "A8-100798",  "sugar",             "VERIFIED"),

    ("Near-Expiry Warning — Lipton Yellow Label Tea (expires 2026-03-28)",
     "01-0132",    "tea",               "VERIFIED_NEAR_EXPIRY"),

    ("COUNTERFEIT — Kellogg's NAFDAC on a fake cosmetic product",
     "A8-4114",    "cosmetics",         "SUBCATEGORY_MISMATCH"),

    ("COUNTERFEIT — Vaseline NAFDAC on fake cooking oil",
     "02-0385",    "cooking oil",       "SUBCATEGORY_MISMATCH"),

    ("COUNTERFEIT — Indomie NAFDAC on fake seasoning cube",
     "01-0877",    "seasoning cube",    "SUBCATEGORY_MISMATCH"),

    ("FAKE — NAFDAC number does not exist in the database",
     "FAKE-9999",  "cereal",            "NOT_FOUND"),

    ("FAKE — Completely made-up number",
     "ZZ-00000",   "beverages",         "NOT_FOUND"),
]


def run_demo(retriever):
    """Run all built-in demo scenarios and print a summary table."""
    from retrieval.regulatory_scorer import compute_verification_score

    _print_header("SabiLens RAG — Full Demo Run")
    print(f"  Running {len(DEMO_SCENARIOS)} scenarios…\n")

    summary = []

    for i, (label, nafdac, cat, expected) in enumerate(DEMO_SCENARIOS, 1):
        records = retriever.retrieve_by_nafdac_no(nafdac)
        result  = compute_verification_score(nafdac, cat, records)

        status   = result["status_code"]
        score    = result["verification_score"]
        matched  = status == expected
        icon     = green("✅ PASS") if matched else red("❌ FAIL")
        s_icon   = _STATUS_ICONS.get(status, status)

        print(f"  [{i:02d}] {icon}  {label}")
        print(f"        NAFDAC: {cyan(nafdac):25}  scanned_as: {cat}")
        print(f"        Status: {s_icon:35}  Score: {_score_bar(score, 20)}")
        print(f"        Summary: {dim(result['summary'][:70])}")
        _print_divider("·")

        summary.append((label, matched, status, score))

    # ── Summary table ─────────────────────────────────────────────────────────
    passed = sum(1 for _, ok, _, _ in summary if ok)
    total  = len(summary)

    _print_header(f"Demo Summary  —  {passed}/{total} scenarios matched expected status")
    for label, ok, status, score in summary:
        icon = green("✅") if ok else red("❌")
        print(f"  {icon}  {label[:55]:55}  {score:.2f}  {status}")
    print()


# ── Interactive menu ──────────────────────────────────────────────────────────

def interactive_menu(retriever):
    """Run an interactive REPL for manual queries."""
    _print_header("SabiLens RAG — Interactive Query Tester")
    print("  Type a command or press Ctrl+C / 'q' to quit.\n")

    MENU = """  Commands:
    1  Verify a product by NAFDAC number + category
    2  Semantic search by product text
    3  Browse products by subcategory
    4  Run all demo scenarios
    5  Show all 15 products in the database
    q  Quit
"""
    print(MENU)

    while True:
        try:
            choice = input(bold("  > ")).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye.")
            break

        if choice in ("q", "quit", "exit"):
            print("  Goodbye.")
            break

        elif choice == "1":
            nafdac = input("  NAFDAC number: ").strip()
            cat    = input("  Scanned as (e.g. 'corn flakes', 'cosmetics'): ").strip()
            verify_product(retriever, nafdac, cat)

        elif choice == "2":
            query = input("  Product text: ").strip()
            n_raw = input("  How many results? [5]: ").strip()
            n     = int(n_raw) if n_raw.isdigit() else 5
            search_products(retriever, query, n)

        elif choice == "3":
            print(dim("  Valid: Cereals and Cereal Products | Cosmetics |"))
            print(dim("         Fats and oils, and Fat Emulsions |"))
            print(dim("         Salts, Spices, Soups, Sauces, Salads and Seasoning |"))
            print(dim("         Beverages | Sweeteners"))
            cat = input("  Subcategory: ").strip()
            browse_category(retriever, cat)

        elif choice == "4":
            run_demo(retriever)

        elif choice == "5":
            # Show everything by doing a wide semantic search
            _print_header("All 15 Products in the Database")
            all_cats = [
                "Cereals and Cereal Products",
                "Cosmetics",
                "Fats and oils, and Fat Emulsions",
                "Salts, Spices, Soups, Sauces, Salads and Seasoning",
                "Beverages",
                "Sweeteners",
            ]
            total = 0
            for cat in all_cats:
                records = retriever.retrieve_by_subcategory(cat, n=20)
                if records:
                    print(f"\n  {bold(cat)}  ({len(records)} products)")
                    _print_divider("·")
                    for r in records:
                        print(f"    {cyan(r.get('nafdac_no_clean','—')):15}"
                              f"  {r.get('product_name','—')}")
                        print(f"    {dim('Expiry:'):17}  {r.get('expiry_date_iso','—')}"
                              f"  │  {r.get('applicant_name','—')}")
                    total += len(records)
            print(f"\n  {bold(f'Total: {total} products indexed')}\n")

        else:
            print(yellow("  Unknown command. Enter 1–5 or q."))

        print(MENU)


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def _load_retriever():
    """
    Initialise the ProductRetriever — loads ChromaDB client and embedding model.
    Prints a helpful error and exits cleanly if ingestion hasn't been run yet.
    """
    print(dim("  Loading retriever (ChromaDB + embedding model)…"))
    try:
        from retrieval.retriever import ProductRetriever
        retriever = ProductRetriever()
    except Exception as exc:
        print(red("\n  ❌  Failed to load the retriever."))
        print(yellow("  Did you run ingestion first?  →  python main.py --mode ingest\n"))
        print(dim(f"  Error detail: {exc}"))
        sys.exit(1)

    count = retriever.store.count()
    if count == 0:
        print(red("\n  ❌  The ChromaDB collection is empty (0 documents)."))
        print(yellow("  Run ingestion first:  python main.py --mode ingest\n"))
        sys.exit(1)

    print(green(f"  ✅  Ready — {count} product(s) indexed in ChromaDB.\n"))
    return retriever


def main():
    parser = argparse.ArgumentParser(
        description="SabiLens RAG — single-file query tester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python rag_query.py
          python rag_query.py --demo
          python rag_query.py --nafdac "A8-4114" --category "corn flakes"
          python rag_query.py --nafdac "A8-4114" --category "cosmetics"
          python rag_query.py --search "indomie chicken noodles"
          python rag_query.py --browse "Cosmetics"
        """),
    )
    parser.add_argument("--nafdac",   metavar="NRN",      help="NAFDAC number to verify")
    parser.add_argument("--category", metavar="CAT",      help="Scanned product category (used with --nafdac)")
    parser.add_argument("--search",   metavar="TEXT",     help="Semantic product text search query")
    parser.add_argument("--browse",   metavar="SUBCAT",   help="Browse all products in a subcategory")
    parser.add_argument("--demo",     action="store_true",help="Run all built-in demo scenarios")
    parser.add_argument("--n",        type=int, default=5, metavar="N", help="Max results for --search (default: 5)")
    args = parser.parse_args()

    print()
    _print_header("SabiLens NAFDAC RAG — Query Tester")

    retriever = _load_retriever()

    # ── Non-interactive modes ─────────────────────────────────────────────────
    if args.demo:
        run_demo(retriever)

    elif args.nafdac:
        cat = args.category or ""
        if not cat:
            cat = input(bold("  Scanned as (e.g. 'corn flakes', 'cosmetics'): ")).strip()
        verify_product(retriever, args.nafdac, cat)

    elif args.search:
        search_products(retriever, args.search, n=args.n)

    elif args.browse:
        browse_category(retriever, args.browse)

    # ── Interactive mode (no flags) ───────────────────────────────────────────
    else:
        interactive_menu(retriever)


if __name__ == "__main__":
    main()