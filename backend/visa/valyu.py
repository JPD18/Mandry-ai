import os
import logging
from typing import List, Dict, Any
from rest_framework import status
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class ValyuAPIException(APIException):
    """Custom exception for Valyu API errors"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Valyu API service temporarily unavailable.'
    default_code = 'valyu_api_error'


def extract_main_query(user_question: str) -> str:
    """
    Extract the main search query from user's question and ensure it's UK-focused for better RAG results
    """
    from services.llm_service import default_llm
    
    try:
        # Use LLM to reformulate the query to be UK-specific
        uk_focused_prompt = f"""Convert this user question into a UK-focused search query for finding official UK government information.

        INSTRUCTIONS:
        1. Keep the main subject and intent of the original question
        2. Add "UK" or "United Kingdom" context where appropriate
        3. Focus on UK government sources and UK-specific information
        4. Make it a concise search query (not a full question)
        5. If it's already UK-focused, improve the search terms
        6. keep it 100 tokens max
        Original question: "{user_question}"

        Return only the UK-focused search query, nothing else."""

        uk_query = default_llm.call(
            uk_focused_prompt, 
            "",
            extra_params={
                "max_tokens": 50,
                "temperature": 0.1  # Low temperature for consistent reformulation
            }
        ).strip()
        
        # Fallback to manual processing if LLM fails or returns empty
        if not uk_query or len(uk_query) < 5:
            raise Exception("LLM returned empty or too short query")
            
        logger.info(f"LLM converted query: '{user_question}' -> '{uk_query}'")
        return uk_query
        
    except Exception as e:
        logger.warning(f"LLM query conversion failed: {str(e)}, falling back to manual processing")
        
        # Fallback to original logic with UK focus added
        question_lower = user_question.lower().strip()
        
        # Remove common question words and extract key terms
        question_starters = [
            "what is", "what are", "how do i", "how to", "can i", "do i need",
            "tell me about", "explain", "help me with", "i need to know about"
        ]
        
        for starter in question_starters:
            if question_lower.startswith(starter):
                question_lower = question_lower[len(starter):].strip()
                break
        
        # Remove question marks and clean up
        query = question_lower.replace("?", "").strip()
        
        # Add UK context if not already present
        if not any(uk_term in query for uk_term in ['uk', 'united kingdom', 'britain', 'british']):
            query = f"UK {query}"
        
        # If query is too short, return original question with UK prefix
        if len(query) < 3:
            return f"UK {user_question}"
        
        logger.info(f"Manual UK-focused query: '{query}' from original question: '{user_question}'")
        return query


def valyu_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search using Valyu API and return normalized results for RAG
    """
    try:
        from valyu import Valyu
        
        # Get API key from environment or use the working key from the test
        api_key = os.getenv('VALYU_API_KEY', 'uEYmO9R7sN8xedZmtYP38qxutV4MD69afLuXWDK2')
        
        # Initialize Valyu client with API key
        valyu = Valyu(api_key=api_key)
        
        # Perform search
        response = valyu.search(
            query,
            search_type="web",                    # Search both proprietary and web sources
            max_num_results=top_k,               # Limit to requested number of results
            relevance_threshold=0.5,             # Only return results with >50% relevance
            max_price=10.0,                      # Maximum cost in dollars
            is_tool_call=True                    # True for AI agents/tools
        )
        
        logger.info(f"Valyu search completed for query: '{query}'")
        
        # Process and normalize the results
        results = []
        
        # Handle different response formats
        if hasattr(response, 'results') and response.results:
            raw_results = response.results
        elif hasattr(response, 'data') and response.data:
            raw_results = response.data
        elif isinstance(response, list):
            raw_results = response
        elif isinstance(response, dict):
            raw_results = response.get('results', response.get('data', []))
        else:
            # Try to iterate over response
            try:
                raw_results = list(response) if response else []
            except:
                raw_results = []
        
        # Normalize each result
        for item in raw_results:
            normalized_result = {}
            
            if hasattr(item, '__dict__'):
                # Handle object responses
                item_data = item.__dict__
            elif isinstance(item, dict):
                item_data = item
            else:
                continue
            
            # Extract title
            normalized_result['title'] = (
                item_data.get('title') or 
                item_data.get('name') or 
                item_data.get('heading') or 
                'Relevant Information'
            )
            
            # Extract URL
            normalized_result['url'] = (
                item_data.get('url') or 
                item_data.get('link') or 
                item_data.get('source_url') or 
                'https://gov.uk'
            )
            
            # Extract content/snippet
            content = (
                item_data.get('snippet') or 
                item_data.get('description') or 
                item_data.get('content') or 
                item_data.get('text') or 
                item_data.get('summary') or
                'No description available'
            )
            
            # Clean and truncate content
            if len(content) > 500:
                content = content[:500] + "..."
            
            normalized_result['snippet'] = content
            
            results.append(normalized_result)
        
        # If no results found, provide relevant fallback
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
    """
    Provide relevant fallback sources when Valyu API fails
    """
    # Determine topic based on query keywords
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['visa', 'travel', 'immigration', 'passport']):
        return [
            {
                'title': 'UK Government Visa Information',
                'url': 'https://gov.uk/check-uk-visa',
                'snippet': 'Check if you need a UK visa, what type of visa you need and how to apply. Official government guidance on visa requirements and application processes.'
            },
            {
                'title': 'Apply for a UK Visa',
                'url': 'https://gov.uk/apply-uk-visa',
                'snippet': 'How to apply for a UK visa, including tourist, business, and other visa types. Complete application guide with requirements and timelines.'
            }
        ]
    else:
        return [
            {
                'title': 'UK Government Official Information',
                'url': 'https://gov.uk',
                'snippet': f'Official UK government information and services related to: {query}. Please verify current information on official government websites.'
            }
        ]


def create_rag_context(query: str, max_sources: int = 3) -> str:
    """
    Create RAG context by searching Valyu and formatting results for LLM
    """
    try:
        # Extract the main query for better search results
        search_query = extract_main_query(query)
        
        # Get search results from Valyu
        search_results = valyu_search(search_query, max_sources)
        
        if not search_results:
            return "No relevant sources found for this query."
        
        # Format context for LLM
        context_parts = ["OFFICIAL SOURCES CONTEXT:"]
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"\nSource {i}: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['snippet']}\n"
            )
        
        context = "\n".join(context_parts)
        logger.info(f"Created RAG context with {len(search_results)} sources")
        return context
        
    except Exception as e:
        logger.error(f"Error creating RAG context: {str(e)}")
        return "Unable to retrieve verification sources at this time."


def get_rag_context_and_sources(user_question: str, max_sources: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    """
    Create RAG context and return both the context string and the source results used
    This ensures the same sources are used for both LLM context and frontend citations
    """
    try:
        # Extract the UK-focused query for better search results
        search_query = extract_main_query(user_question)
        
        # Get search results from Valyu using the UK-focused query
        search_results = valyu_search(search_query, max_sources)
        
        if not search_results:
            logger.warning("No search results found, using fallback sources")
            search_results = get_fallback_sources(user_question)
        
        # Format context for LLM
        context_parts = ["OFFICIAL SOURCES CONTEXT:"]
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"\nSource {i}: {result['title']}\n"
                f"URL: {result['url']}\n"
                f"Content: {result['snippet']}\n"
            )
        
        context = "\n".join(context_parts)
        logger.info(f"Created RAG context with {len(search_results)} sources using UK-focused query: '{search_query}'")
        
        return context, search_results
        
    except Exception as e:
        logger.error(f"Error creating RAG context and sources: {str(e)}")
        fallback_sources = get_fallback_sources(user_question)
        return "Unable to retrieve verification sources at this time.", fallback_sources


def get_rag_enhanced_prompt_with_sources(user_question: str, max_sources: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    """
    Create an enhanced system prompt with RAG context and return the sources used
    This replaces the old get_rag_enhanced_prompt to ensure citation consistency
    """
    rag_context, sources = get_rag_context_and_sources(user_question, max_sources)
    
    enhanced_prompt = f"""You are a knowledgeable travel and visa assistant for the united kingdom with access to official sources.

    {rag_context}

    INSTRUCTIONS:
    1. Base your answer primarily on the official sources provided above
    2. Use **markdown formatting** for emphasis (bold, italic, lists, etc.)
    3. Include inline citations using [Source 1], [Source 2], etc. when referencing information
    4. Structure your response with clear headings and bullet points where appropriate
    5. If the sources don't contain enough information, clearly state this limitation
    6. Always recommend checking the most current official government websites
    7. Be helpful but emphasize the importance of verifying information with official sources
    8. Provide accurate, up-to-date information based on the context provided
    9. Format your response for readability with proper paragraphs and spacing

    RESPONSE FORMAT:
    - Use **bold** for important terms and requirements
    - Use bullet points or numbered lists for step-by-step information
    - Include [Source X] citations immediately after relevant information
    - End with a verification reminder

    User Question: {user_question}

    Please provide a comprehensive, well-formatted answer using the official sources above."""

    return enhanced_prompt, sources


def get_rag_enhanced_prompt(user_question: str, max_sources: int = 3) -> str:
    """
    Create an enhanced system prompt with RAG context (backward compatibility)
    For new code, use get_rag_enhanced_prompt_with_sources() to ensure citation consistency
    """
    enhanced_prompt, _ = get_rag_enhanced_prompt_with_sources(user_question, max_sources)
    return enhanced_prompt


# Compatibility functions for existing code
def sync_valyu_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Compatibility function for existing code"""
    return valyu_search(query, top_k)


def sync_get_rag_context(query: str, max_sources: int = 3) -> str:
    """Compatibility function for existing code"""
    return create_rag_context(query, max_sources)


def get_rag_context(query: str, max_sources: int = 3) -> str:
    """Compatibility function for existing code"""
    return create_rag_context(query, max_sources) 