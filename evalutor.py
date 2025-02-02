
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from typing import List,Tuple,overload
from Utils import Utils
import asyncio


class Evalutor:
    llm:BaseChatModel



    __cover_letter_prompt='''
        Given the title and description of a job, write a cover letter to be used on upwork that explains why I am a good fit for the job.
        Include emojis as much as possible to make the cover letter more engaging.
        Given a brief description of me,my name,my skills,and projects i worked on ,write a cover letter for the job.
        
        Brief description: Hi there! 👋 I'm a Full-Stack Developer with 1+ years of experience in building scalable, high-performance web and mobile applications. I specialize in creating solutions that ✨ exceed expectations and align with your business goals.

        My Skills:{skills}

        My Projects:{projects}

        My name: Ahmed Said


        ### Notes
        - Don't start with "Dear [Client],".
        - Use so many emojis to illustrate your points.
        - only use the given skills and projects to write the cover letter.
        - use emojis instead of '*'.
        - don't add links for any of the projects.
        - don't add your chain of thoughts or <think>.
        '''

    class Evaluations(BaseModel):

        '''
        Given a description of my skills and abilites in the field of software engineering, and the title and description of a job,
        decide whether I am a good fit for the job.
        Return True if the job is a good fit for me based on my skills, False otherwise.


        ### Example:

            Title: Logo Design and Branding

            Description: I need a simple and modern logo for a new project called TechWave Innovations 
            it's a Technology and Software Development company. The design should be clean, professional,
            and adaptable for use across different platforms (website, social media, etc.).
            
            Requirements:Must provide logo in PNG and vector formats (AI or EPS)
            Please include 2-3 logo concepts to choose from
            
            To Apply: Please submit your portfolio or examples of previous logo designs.

            result: False
        '''


        result:bool=Field(description='Whether the job is a good fit for me based on my skills.Return True if am a good fit otherwise False.')


    def __init__(self,model:BaseChatModel=ChatOllama(model="gemma2:2b"),skills=[],projects=[],system_prompt='',cover_letter_model=None):
        self.llm=model
        self.system_prompt=system_prompt
        self.prompt=ChatPromptTemplate([('system',self.system_prompt),('user','{input}')])
        self.structured_llm=self.llm.with_structured_output(self.Evaluations)
        self.prompt_augmented_llm=self.prompt | self.structured_llm
        self.__cover_letter_prompt=Utils.format_prompt(self.__cover_letter_prompt,skills,projects)
        self.cover_model=cover_letter_model

    
    async def __evalute(self,title,description)->bool:
        try:
            output=await self.prompt_augmented_llm.ainvoke(input=f'Title: {title}\nDescription: {description}')
        except Exception as e:
           print('An error occured while evaluating',e)
           return self.Evaluations(result=False)
        return output
        
    async def __call__(self, titles_descriptions:List[Tuple[str,str]]):
        return await asyncio.gather(*[self.__evalute(title,description) for title,description in titles_descriptions])



    async def generate_cover_letters(self,titles_descriptions:List[Tuple[str,str]]):
        cover_letters=[]
        for title,description in titles_descriptions:
            chatPrompt=ChatPromptTemplate([('system',self.__cover_letter_prompt),('user','{input}')])
            augmented_llm=chatPrompt | self.cover_model
            cover_letters.append(augmented_llm.ainvoke(input=f'Job Title: {title}\nJob Description: {description}'))

        return await asyncio.gather(*cover_letters)