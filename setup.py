from setuptools import find_packages, setup
from typing import List

def get_requirements()-> List[str]:
    
    '''
    Docstring for get_requirements
    This function returns all requirements in the list format
    
    :return: Description
    :rtype: List[str]
    '''
    
    requirements_list:List[str] = []
    HYPEN_E_DOT = '-e .'
    try:
        with open('requirements.txt', 'r') as file_obj:
            lines = file_obj.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement!= HYPEN_E_DOT:
                    requirements_list.append(requirement)
        
    except Exception as e:
        print(f"Error Occured : {e}")
    
    return requirements_list

setup(
    name='NetworkSecurity',
    version='0.0.1',
    author='Harish',
    author_email='getintouchwithharish@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)
        