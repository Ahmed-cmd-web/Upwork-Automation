from langchain_ollama import ChatOllama
from extractor import SelenuimExtractor
from evalutor import Evalutor
import pywhatkit
import asyncio
import Utils
import os



MAX_JOB_POSTS=5




email=os.getenv('EMAIL')
password=os.getenv('PASSWORD')
secret_answer=os.getenv('SECRET_ANSWER')
phone_number=os.getenv('PHONE_NUMBER')

url='https://www.upwork.com/nx/find-work/'



username_field_id='login_username'
username_button_id='login_password_continue'
password_field_id='login_password'
password_button_id='login_control_continue'
load_more_button_data_test='load-more-button'
link_prefix='https://www.upwork.com'



skills=[
    'Python',
    'Java',
    'JavaScript',
    'HTML',
    'CSS',
    'SQL',
    'Git',
    'React.js',
    'React Native',
    'Expo',
    'Redux',
    'Node.js',
    'Express.js',
    'MongoDB',
    'PostgreSQL',
    'Django',
    'Djangorestframework',
    'LLMs',
    'Machine Learning',
    'Deep Learning',
    'AWS'
]

projects=[
    ('Deal Hunter','A web application that takes a keyword of a product, scrapes products from trendyol,and converts the prices to EGP in seconds.',['Django','Djangorestframework','Python','HTML','CSS','JavaScript']),
    ('Covid 19 tracker','A web application that displays the number of cases, deaths, and recoveries of Covid 19 in each country.',['React','Node.js','Express.js','MongoDB','HTML','CSS','JavaScript']),
    ('Face Recognition','A web application that detects faces in images and videos.',['React','Node.js','Express.js','MongoDB','HTML','CSS','JavaScript','Machine Learning']),
    ('E-commerce website','A web application that allows users to buy and sell products.',['React','Node.js','Express.js','MongoDB','HTML','CSS','JavaScript']),
    ('WhatsApp mobile clone','A cross platform mobile application that allows users to chat with each other in real-time.',['React Native','Expo','Node.js','Express.js','MongoDB','HTML','CSS','JavaScript']),
]


system_prompt='''
You are an expert software engineer with a strong background in software development and programming. 
You have experience working with a variety of programming languages and tools.

Given below my skills and the projects I worked on in the field of software engineering,
decide whether I will be able to do the job given the following skils and projects.

My Skills:{skills}

My Projects:{projects}

'''


llm = ChatOllama(model="llama3.2")
cover_letter_model=ChatOllama(model="llama3.2")

async def evalute_and_create_letter(jobs):

    ev=Evalutor(model=llm,system_prompt=Utils.format_prompt(system_prompt,skills,projects),skills=skills,projects=projects,cover_letter_model=cover_letter_model)
    Utils.clean_text(jobs)

    evalutions=await ev([(job['title'],job['description']) for job in jobs])

    
    using=[jobs[index] for index,evalution in enumerate(evalutions) if evalution is not None and evalution.result is True]

    cover_letters=await ev.generate_cover_letters([(job['title'],job['description']) for job in using])
    cover_letters=[c.content for c in cover_letters]


    return using,cover_letters

jobs=SelenuimExtractor(url,email,password,secret_answer)
extracted_jobs=jobs.extract(MAX_JOB_POSTS)
jobs,cover_letters= asyncio.run(evalute_and_create_letter(extracted_jobs))



message=''
for job,cover_letter in zip(jobs,cover_letters):
        message+=f"Title: {job['title']}\n\nDescription: {job['description']}\n\nCountry:{job['country']}\n\nCover Letter: *{cover_letter}*\n\nLink: {link_prefix}{job['link']}\n\n{"="*50}\n\n"
pywhatkit.sendwhatmsg_instantly(phone_number,message,tab_close=True,close_time=10)


