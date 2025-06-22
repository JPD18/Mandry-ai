import os
import logging
from typing import List, Dict, Any
from services.exceptions import SearchServiceException as _BaseSearchException

logger = logging.getLogger(__name__)

# Preserve original exception name for backwards compatibility
class ValyuAPIException(_BaseSearchException):
    """Exception alias retained for external callers."""

    default_detail = "Valyu API service temporarily unavailable."
    default_code = "valyu_api_error"


# --------------------------------------------------------------------------------------
# Core helper functions (migrated from visa.valyu)
# --------------------------------------------------------------------------------------

def extract_main_query(user_question: str) -> str:
    """Extract the main search query from user's question and ensure it's UK-focused for better RAG results"""
    from services.llm_service import default_llm
    try:
        uk_focused_prompt = f"""Convert this text into a  search question for finding official government information.

        INSTRUCTIONS:
        1. Keep the main subject and intent of the original question
        2. If the user is asking about a specific country, use that country in the search question
        4. if there is any information about the user's profile, include it in the search question
        3. Focus on government sources andc information
        4. Make it a concise search question THAT FRAMES THE QUERY AS A QUESTION e.g. what is where are who is etc
        6. keep it 100 tokens max
        Original question: "{user_question}"

        Return only the search question, nothing else."""

        uk_query = default_llm.call(
            uk_focused_prompt,
            "",
            extra_params={
                "max_tokens": 100,
                "temperature": 0.1
            }
        ).strip()
        logger.info(f"LLM converted query: '{user_question}' -> '{uk_query}'")
        if not uk_query or len(uk_query) < 5:
            raise Exception("LLM returned empty or too short query")
        logger.info(f"LLM converted query: '{user_question}' -> '{uk_query}'")
        return uk_query
    except Exception as e:
        logger.warning(f"LLM query conversion failed: {str(e)}, falling back to manual processing")
        question_lower = user_question.lower().strip()
     
        query = question_lower.replace("?", "").strip()
        if not any(uk_term in query for uk_term in ['uk', 'united kingdom', 'britain', 'british']):
            query = f"UK {query}"
        if len(query) < 3:
            return f"UK {user_question}"
        logger.info(f"Manual UK-focused query: '{query}' from original question: '{user_question}'")
        return query


def valyu_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search using Valyu API and return normalized results for RAG"""
    try:
        from valyu import Valyu  # type: ignore
        api_key = os.getenv('VALYU_API_KEY', 'KctkEVR69Xaug36lCfW4kngBvEnUzS81a7yT7wd7')
        valyu = Valyu(api_key=api_key)
    
        response = valyu.search(
            query,
            search_type="web",
            max_num_results=top_k,
            relevance_threshold=0.5,
            max_price=10.0,
            is_tool_call=True
        )
        logger.info(f"Valyu search completed for query: '{query}'")

        results: List[Dict[str, Any]] = []
        if hasattr(response, 'results') and response.results:
            raw_results = response.results
        elif hasattr(response, 'data') and response.data:
            raw_results = response.data
        elif isinstance(response, list):
            raw_results = response
        elif isinstance(response, dict):
            raw_results = response.get('results', response.get('data', []))
        else:
            try:
                raw_results = list(response) if response else []
            except Exception:
                raw_results = []

        for item in raw_results:
            normalized_result: Dict[str, Any] = {}
            item_data = item.__dict__ if hasattr(item, '__dict__') else item if isinstance(item, dict) else {}
            if not item_data:
                continue
            normalized_result['title'] = (
                item_data.get('title') or item_data.get('name') or item_data.get('heading') or 'Relevant Information'
            )
            normalized_result['url'] = (
                item_data.get('url') or item_data.get('link') or item_data.get('source_url') or 'https://gov.uk'
            )
            content = (
                item_data.get('snippet') or item_data.get('description') or item_data.get('content') or item_data.get('text') or
                item_data.get('summary') or 'No description available'
            )
            if len(content) > 500:
                content = content[:500] + "..."
            normalized_result['snippet'] = content
            results.append(normalized_result)
        if not results:
            logger.warning(f"No results returned from Valyu for query: '{query}', providing fallback")
            results = get_fallback_sources(query)
        logger.info(f"Returning {len(results)} normalized results for RAG")
        return results
    except ImportError:
        logger.error("Valyu SDK not available")
        return get_fallback_sources(query)
    except Exception as e:
        logger.error(f"Valyu search error: {str(e)}")
        return get_fallback_sources(query)


def get_fallback_sources(query: str) -> List[Dict[str, Any]]:
    """Provide relevant fallback sources when Valyu API fails"""
    query_lower = query.lower()
    if any(word in query_lower for word in ['visa', 'travel', 'immigration', 'passport']):
        return [
            {
                'title': 'UK Government Visa Information',
                'url': 'https://gov.uk/check-uk-visa',
                'snippet': 'Check if you need a UK visa, what type of visa you need and how to apply.'
            },
            {
                'title': 'Apply for a UK Visa',
                'url': 'https://gov.uk/apply-uk-visa',
                'snippet': 'How to apply for a UK visa, including tourist, business, and other visa types.'
            }
        ]
    return [
        {
            'title': 'UK Government Official Information',
            'url': 'https://gov.uk',
            'snippet': f'Official UK government information and services related to: {query}. '
                       'Please verify current information on official government websites.'
        }
    ]


def create_rag_context(query: str, max_sources: int = 3) -> str:
    try:
        search_query = extract_main_query(query)
        search_results = valyu_search(search_query, max_sources)
        if not search_results:
            return "No relevant sources found for this query."
        context_parts = ["OFFICIAL SOURCES CONTEXT:"]
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"\nSource {i}: {result['title']}\nURL: {result['url']}\nContent: {result['snippet']}\n"
            )
        context = "\n".join(context_parts)
        logger.info(f"Created RAG context with {len(search_results)} sources")
        return context
    except Exception as e:
        logger.error(f"Error creating RAG context: {str(e)}")
        return "Unable to retrieve verification sources at this time."


def get_rag_context_and_sources(user_question: str, max_sources: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    try:
        search_query = extract_main_query(user_question)
        logger.info(f"Search query: {search_query}")
        search_results = valyu_search(search_query, max_sources)
        if not search_results:
            logger.warning("No search results found, using fallback sources")
            search_results = get_fallback_sources(user_question)
        context_parts = ["OFFICIAL SOURCES CONTEXT:"]
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"\nSource {i}: {result['title']}\nURL: {result['url']}\nContent: {result['snippet']}\n"
            )
        context = "\n".join(context_parts)
        logger.info(
            f"Created RAG context with {len(search_results)} sources using UK-focused query: '{search_query}'"
        )
        return context, search_results
    except Exception as e:
        logger.error(f"Error creating RAG context and sources: {str(e)}")
        fallback_sources = get_fallback_sources(user_question)
        return "Unable to retrieve verification sources at this time.", fallback_sources


def get_rag_enhanced_prompt_with_sources(user_question: str, max_sources: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    logger.info(f"Getting RAG enhanced prompt with sources for user question: {user_question}")
    rag_context, sources = get_rag_context_and_sources(user_question, max_sources)
    enhanced_prompt = f"""You are a knowledgeable travel and visa assistant with access to official sources.

    {rag_context}

    INSTRUCTIONS:
    1. Base your answer primarily on the official sources provided above
    2. Use **markdown formatting** for emphasis (bold, italic, lists, etc.)
    3. Include inline citations using [Source 1], [Source 2], etc.
    4. Structure your response with clear headings and bullet points
    5. If the sources don't contain enough information, clearly state this limitation
    6. Always recommend checking the most current official government websites
    7. Provide accurate, up-to-date information based on the context provided

    User Question: {user_question}

    Please provide a comprehensive, well-formatted answer using the official sources above."""
    return enhanced_prompt, sources


def get_rag_enhanced_prompt(user_question: str, max_sources: int = 3) -> str:
    enhanced_prompt, _ = get_rag_enhanced_prompt_with_sources(user_question, max_sources)
    return enhanced_prompt

# Compatibility helpers for legacy code

def sync_valyu_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    return valyu_search(query, top_k)

def sync_get_rag_context(query: str, max_sources: int = 3) -> str:
    return create_rag_context(query, max_sources)

def get_rag_context(query: str, max_sources: int = 3) -> str:
    return create_rag_context(query, max_sources)

# --------------------------------------------------------------------------------------
# OO wrapper for future LangGraph tooling
# --------------------------------------------------------------------------------------

class SearchService:
    """Thin OO façade exposing search utilities as instance methods."""

    # Map existing functions to instance-callable methods for consistency with other services
    extract_main_query = staticmethod(extract_main_query)
    valyu_search = staticmethod(valyu_search)
    create_rag_context = staticmethod(create_rag_context)
    get_rag_context_and_sources = staticmethod(get_rag_context_and_sources)
    get_rag_enhanced_prompt_with_sources = staticmethod(get_rag_enhanced_prompt_with_sources)
    get_rag_enhanced_prompt = staticmethod(get_rag_enhanced_prompt)
    sync_valyu_search = staticmethod(sync_valyu_search)
    sync_get_rag_context = staticmethod(sync_get_rag_context)
    get_rag_context = staticmethod(get_rag_context)


# Singleton export for convenience & future dependency injection
default_search_service = SearchService()

# Public alias re-export so callers can do `from services.search_service import SearchServiceException`
SearchServiceException = _BaseSearchException 