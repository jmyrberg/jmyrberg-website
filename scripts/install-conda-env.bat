echo Installing...
set NAME=jmyrberg-website
call conda env remove -n %NAME% -y
call conda create -n %NAME% python=3.7 -y
call activate %NAME%
call pip install -r ./functions/doc_context_similarity/requirements.txt -r ./functions/get_food_recommender/requirements.txt -r ./functions/post_food_recommender/requirements.txt -r ./functions/maximum_flows/requirements.txt -r ./functions/contact/requirements.txt -r ./functions/requirements-dev.txt
echo Installation done!
pause