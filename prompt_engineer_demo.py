from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


def main():
    prompt_message = """
        You are an expert prompt engineer. Based on the following input, create a detailed and structured prompt for an AI agent:
    
        Input: "{input_description}"
        
        The prompt should include:
        1. Role: Clearly define the role the AI should take.
        2. Task: Describe the task the AI needs to perform.
        3. Guidelines: Any specific rules or considerations.
        4. Expected Output: Describe what the final output should look like.
        
        Ensure the prompt is clear, actionable, and optimized for the AI to perform well.
        Even if any of the 4 topics (Role, Task, Guidelines & Expected Output) is not directly included in the input description,
        try to infer it. E.g. if the task is to write code in python, the role could be an expert Python Developer or an expert Software Engineer in Python or something similar. 
         
        If the input description refer to something that is not defined, or that sounds like a variable, use it as an input to the prompt.
        For example, if you are told to use "notes" as an input to the prompt, the prompt should contain {{notes}}. 
        Include such input variables in the prompt description. However, only include them ONCE in the whole text.
        If you want to refer to them a second time, do it without the curly brackets. 
        Input variables will be used to pass additional information in the prompt, and should therefore only be mentioned once in the prompt.
        However, don't mention that they are input variables, as they will be replaced with different content anyways.
        Just incorporate them in natural language, or even just write the variable in curly brackets as a single-word-paragraph.  
        Don't misinterpret them with variables that are mentioned in input description.
          Input variables should only be included if it is required to understand the prompt and could not be done without.
          If the prompt can be understood by mentioning the variable in natural language instead of replacing it with actual content, it should be written in natural language. 
         
        --------------
         
        Example on when to introduce a variable:
        Input description: "Organize notes. Use notes as input variable"
        Possible result: "You are a helpful assistant, organizing notes. 
        Your task is to summarize and organize these notes in a meaningful structure. 
          {{notes}}
          
        Guidelines:
        - Do not make things up
        - Only use content provided in the notes
        - Use clear and concise language
        
        Expected Output: The final output should be a well-organized summary of the notes, such that someone can easily read and understand them. It should include:
        - Structured into topic groups
        - Each topic should be summarized in bullet points
        - A nice readable structure
        - Essential information about the notes           
         
         --------------
         Example on when not to introduce a variable:
         Input description: "Write a python function that prints the content of the variable 'n' concatenated with a prefix 'p'"
         This example mentions 2 variables, but both of them relate to the description and should remain variables.
         Neither 'n' nor 'p' should be replaced with content, therefore they should be mentioned as they are.
         They must NOT be mentioned as {{n}} or {{p}}   
          
         --------------
        
        Don't write any additional text before or after the prompt. Just the prompt ist fine. 
         Also, formulate it as if you were talking to the AI agent and write whole sentences.
         For example a start of your result could look like this: "You are a professional Content Creator..."    
        
         """
    model = OllamaLLM(model="llama3.1:8b", temperature=0.05)
    prompt = PromptTemplate.from_template(prompt_message)
    parser = StrOutputParser()
    chain = prompt | model | parser
    for description in [
        "Write a debate about Frontend vs Backend devs.",
        "Write some code in python that creates the Fibonacci sequence until Input variable n.",
        "Summarize the provided content. Use content as an input variable"
    ]:
        answer = chain.invoke({"input_description": description})
        print(answer)
        print()
        print()
        print()
        print()


if __name__ == "__main__":
    main()
