cd dist
del /q *.*
cd ..
python -m pip install --upgrade pip setuptools wheel build twine
python setup.py sdist bdist_wheel

python -m twine upload --verbose --config-file .pypirc --repository publico dist/*