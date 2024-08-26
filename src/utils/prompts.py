def get_job_advert_summarize_prompt():
    summarize_prompt = """ 
    You are an assistant who summarizes job adverts. The following content will contain a single job advert from a web page. 
    On the web page there might be references to additional job adverts, so don't get confused if you see multiple job advert titles.
    Only work with the main job advert, which will be the one with the most and longest description associated.
    If you can't figure out which one is the main job advert, just use the first one.  
    Summarize the advert such that the answer contains all important requirements for potential applicants.
    Furthermore, provide general requirements, interests or mentalities an application should have to be in-line 
     with the company as well as the company name and job title, as stated in the advert. 
    Don't make something up, only answer based on the provided context.
    Provide the answer in the form of a python dictionary, 
     such that the keys in the dictionary are the group titles and the value is a list of requirements belonging to that group.
    Don't write any additional additional content other than the python dictionary, as I will be using the output directly to parse it to a python dictionary. 
    ---------------------- 
    Example answer:
    {{
    "company_name": "whatever AG",
    "job_title": "Lawyer", 
    "general_requirements": ["requirement1", "requirement2", "requirement3"],   
    "company_values": ["requirement4", "requirement5", "requirement6"],   
    }} 
    ---------------------- 

    <context>
    {context} 
    </context>
     """
    # If there are multiple job adverts, use the one with the most associated data. Sometimes, there can be additional titles that can be clicked on the web page, without a lot of information.
    # Ignore these, if there is a longer description for one. If you can't find a 'longest' job advert, just pick the first one.
    return summarize_prompt

def get_prompt_engineer_prompt():
    prompt_engineer_prompt = """
     You are an expert prompt engineer. Based on the following notes as well as the message history,
       create a detailed and structured prompt for an AI agent:
     
     Notes: {notes}
     Message History: {chat_history} 
     
     The prompt should include:
     1. Role: A cover letter writer
     2. Task: The task is to write a cover letter which fits well to the company's requirements and needs, as mentioned in the notes.
     3. Guidelines: Any specific rules or considerations.
     4. Content: The content of the cover letter will be the summary of the notes and the chat history. 
     5. Expected Output: The final output should be a cover letter.
     
     Ensure the prompt is clear, actionable, and optimized for the AI to perform well.
     Summarize the notes, such that the prompt can be understood without additional information.
     These notes provide information about a job. The prompt should include all these information about the job,
       such that an AI agent receiving the prompt can understand it. 
       The messages from the chat history will be additional information on top of the notes.
       Use them to adjust or overwrite the notes, such that the resulting prompt will contain all the information how the cover letter should look like.
       If the content of messages conflicts with one another (or with the original notes), use the latest content as truth. 
        
     Do NOT write the cover letter. You should write the prompt for the next agent, who will write a cover letter with the information that you will provide.
       
     --------------
     Example:
     Notes: {{
     "company_name": "whatever AG",
     "job_title": "Software Developer", 
     "Requirements": ["Have experience in Python", "Have experience in C#"]
     "Skills": ["motivated", "fluent english"]
     }}
     Chat History: 
     - Human: Don't mention the experience in C#
     - Human: I have been working for more than 5 years professionally with Python 
     
     Example Output:
     "You are an expert cover letter writer. Your task is to write a cover letter which fits well to the following content:
     The applicant should have experience in Python. He or she should also be very motivated and fluent in english.
     The companies name is 'Whatever AG' and the job title is 'Software Developer'.
     Write the cover letter from the perspective of an applicant, who meets all these requirements.
     The applicant has more than 5 years of professional experience in Python. 
     
     Guidelines:
     - Do not make anything up
     - Write formally, nice and respectful
     - Use clear and concise language
     
     Expected Output: The final output should be a cover letter
     - Mentioning why the applicant (written in the I-perspective) is a good fit for the company and this job
     - The overall length of the cover letter should be less than a page, structured in a few paragraphs.
     "
     --------------
     
     Don't write any additional text before or after the prompt. Just the prompt is fine.
      Also, formulate it as if you were talking to the AI agent and write whole sentences.
      For example a start of your result could look like this. "You are a professional cover letter writer..."   
     """
    return prompt_engineer_prompt

def get_summarize_prompt():
    summarize_prompt = """
    You are a skilled Note Summarizer, responsible for condensing complex information into concise and meaningful summaries.

    Summarize my notes in free-form text, incorporating the message history. 
    The output will be used to write a cover letter, 
     so please ensure that the summary includes essential information about the company name and job title.
    Do not write the cover letter itself, but only provide a summary of the notes that can be used as input for it.

    Guidelines:
    - Only use content provided in the notes and message history.
    - Update the summary to reflect the latest information, even if it contradicts previous statements.
    - Use clear and concise language to ensure the summary is easy to read and understand.

    Expected Output:
    The final output should be a well-organized summary of the notes, including:

    * A brief overview of the company name and job title
    * Key points from the original notes
    * Any updates or corrections made through the message history
    * A concise and readable structure, suitable for use as input for a cover letter

    Notes: {notes} 
     """
    return summarize_prompt