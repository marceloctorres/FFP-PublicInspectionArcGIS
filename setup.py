import setuptools
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()    
 
setuptools.setup(name='DemoConecteseSigPy', 
        version='0.0.0.2',
        author='Esri Colombia',
        author_email='mtorres@esri.co',
        license='MIT',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/marceloctorres/DemoConecteseSigPython',
        description=('Herramientas Demostración para el Conectese con SIG - ArcGIS Pro.'),
        python_requires= '>=3.6.10',
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'License :: OSI Approved :: MIT License',
            'Operating System :: Microsoft :: Windows :: Windows 10',
            'Operating System :: MacOS',
            'Operating System :: Other OS',
            'Natural Language :: Spanish'
        ],
        package_dir={"": "src"},
        packages = setuptools.find_packages(where="src"),
        package_data={'DemoConecteseSigPy':[
                    '*.json',
                    'esri/toolboxes/*',  
                    'esri/arcpy/*', 
                    'esri/help/gp/*',  
                    'esri/help/gp/toolboxes/*', 
                    'esri/help/gp/messages/*'] 
                    }, 
      )