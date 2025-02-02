


class Utils:


    @classmethod
    def format_prompt(self,
                      prompt,skills,projects):
        return prompt.format(skills="".join([f'\n   - {skill}' for skill in skills]),projects=''.join([f'\n    title: {title}\n    description: {description}\n    skills: {", ".join(skills)}\n' for title,description,skills in projects]))




    @classmethod
    def clean_text(data):
        for d in data:
            for key,v in d.items():
                d[key]=v.encode('UTF-8','ignore').decode('UTF-8')