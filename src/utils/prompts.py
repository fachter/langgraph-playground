def get_job_advert_summarize_prompt():
    summarize_prompt = """ 
    You are an assistant who summarizes job adverts. The following content will contain a single job advert from a web page. Therefore it is formatted as HTML and CSS with some JavaScript. 
    Summarize the advert such that the answer contains all important requirements for potential applicants.
    Furthermore, provide general requirements, interests or mentalities an application should have to be in-line with the company, as stated in the advert.
    Don't make something up, only answer based on the provided context.
    Provide the answer in the form of a python dictionary, 
     such that the keys in the dictionary are the group titles and the value is a list of requirements belonging to that group.
    Don't write any additional additional content other than the python dictionary, as I will be using the output directly to parse it to a python dictionary.
    Example answer:
    {{
    "title1": ["requirement1", "requirement2", "requirement3"],   
    "title2": ["requirement4", "requirement5", "requirement6"],   
    }} 

    <context>
    {context} 
    </context>
     """
    return summarize_prompt
