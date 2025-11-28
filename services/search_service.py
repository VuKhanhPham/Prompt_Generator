def search_prompts(prompts, keyword):
    """
    Search prompts by keyword in purpose, keywords, and prompt text fields.
    Returns results sorted by score (highest first).
    """
    if not keyword or not keyword.strip():
        # If empty keyword, return all prompts sorted by score
        return sorted(prompts, key=lambda x: x.get('score', {}).get('total', 0), reverse=True)
    
    keyword_lower = keyword.lower().strip()
    results = []
    
    for prompt in prompts:
        # Search in purpose, keywords, and prompt text
        purpose = (prompt.get('purpose', '') or '').lower()
        keywords = (prompt.get('keywords', '') or '').lower()
        prompt_text = (prompt.get('prompt', '') or '').lower()
        
        # Check if keyword appears in any of these fields
        if (keyword_lower in purpose or 
            keyword_lower in keywords or 
            keyword_lower in prompt_text):
            results.append(prompt)
    
    # Sort by score (highest first)
    return sorted(results, key=lambda x: x.get('score', {}).get('total', 0), reverse=True)
