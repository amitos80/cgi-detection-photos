## Shell/Terminal Frequently

1. Calculate how many files are left to process in order to complete training on dataset
   ***Command:``` Shell jq '(.chunks | flatten | length) - (.image_tracking | keys | length)' cgi-detector-service/scripts/training_progress.json [current working directory /Users/amit/Projects/cgi-detection-photos] (Recalculating the number of files left to process by subtracting the number of tracked images from the total number of images in all chunks.)```
   ***Syntax Example:``` [CWD] ✗ jq '(.chunks | flatten | length) - (.image_tracking | keys | length)' cgi-detector-service/scripts/training_progress.json .```
   ***Result Example: ```94437```
