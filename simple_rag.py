import re

def read_knowledge_base(file_path):
    """
    Reads the content of the knowledge base file.
    Returns the content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def search_knowledge_base(content, query):
    """
    Performs a simple keyword-based search in the content.
    Returns relevant sentences containing the query keywords.
    """
    if not content:
        return []
    
    # Split content into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Convert query to lowercase and split into keywords
    keywords = query.lower().split()
    
    # Find sentences containing any of the keywords
    relevant_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in keywords):
            relevant_sentences.append(sentence.strip())
    
    return relevant_sentences

def main():
    # File path for the knowledge base
    knowledge_base_file = "love_live_style_notes.txt"
    
    # Read the knowledge base
    content = read_knowledge_base(knowledge_base_file)
    if not content:
        return
    
    # Get user query
    print("\nWelcome to the Love Live! Sunshine!! Style Guide!")
    print("Enter your query about the animation style (e.g., 'Tell me about character movement'):")
    user_query = input("> ")
    
    # Search for relevant information
    results = search_knowledge_base(content, user_query)
    
    # Display results
    if results:
        print("\nRelevant information found:")
        for i, sentence in enumerate(results, 1):
            print(f"\n{i}. {sentence}")
    else:
        print("\nNo relevant information found for your query.")

if __name__ == "__main__":
    main() 