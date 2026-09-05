from typing import Any

SHIP_30_PROMPT_TEMPLATE = """You are an expert ghostwriter trained in the Ship 30 for 30 methodology.
Transform the provided source transcripts and context into a high-impact, actionable essay.

### Structural Requirements:
1. Target Word Count: Approximately 1,250 words.
2. The Hook (first 2-3 lines): a counterintuitive product/growth truth or urgent operational tension.
3. Formatting:
   - High skimmability using short paragraphs (1 to 3 sentences maximum).
   - Clear Markdown headers (H2 and H3).
   - Bold anchor words at the start of bullet points.
4. Grounded Substance:
   - Draw strictly upon the insights shared by guests in the context below.
   - Attribute specific strategies to the corresponding guest/episode.
5. Actionable Conclusion: end with a step-by-step checklist or implementation framework.

Wrap the final essay in an artifact tag so it can be rendered in the side panel:
<artifact type="markdown" title="...">
...essay...
</artifact>

Context Material:
{context_data}

User Request:
{user_query}
"""


def build_ship30_prompt(user_query: str, retrieved_chunks: list[dict[str, Any]]) -> str:
    if not retrieved_chunks:
        formatted_context = "(No relevant transcript chunks were found for this query.)"
    else:
        formatted_context = "\n\n".join(
            f"--- Episode: {c['episode']} (Guest: {c['guest']}) ---\n{c['text']}"
            for c in retrieved_chunks
        )
    return SHIP_30_PROMPT_TEMPLATE.format(context_data=formatted_context, user_query=user_query)
