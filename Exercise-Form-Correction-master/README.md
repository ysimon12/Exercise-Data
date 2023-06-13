# Exercise-Form-Correction

Web-app that allows users to upload a video of themselves performing a squat and get feedback on it. While also allowing them to keep progress about it.

### How to run
Navigate to the website directory. `cd website`<br>
Execute the following command `python manage.py runserver`

From that you'll be able to use the website.


How to empty and completely restart website.
Navigate to the website directory. `cd website`<br>
Execute the following command `python manage.py flush` This will flush the databases.<br>
Add the following code to video/helpers.JointDetection.py at the bottom `writeToJSONFile(trainAllVideos('videos')`<br>
Go back to base directory of website.<br>
Start up website `python manage.py runserver`<br>
Go to localhost:8000/formcheck/script. This will add training data plus its feedback to databases.<br>
You're all set.<br>
