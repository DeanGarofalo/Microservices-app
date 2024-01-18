# Summary

This project was created by following along with a guide from freeCodeCamp to build a Microservice application using Python and Kubernetes.
I had just recently picked up Python and wanted to stretch my legs by actually developing a microservice app instead of just consuming it, in effort of getting a better understanding of working in a distributed microservice environment.

This application will convert Videos into MP3 files with each core component distributed as a specific micro-service.


# Flow

The user uploads a video file which first hits the Gateway-service (a Flask webserver). The Gateway is responsible for calling the Authentication-service to verify the user (stored in a MySQL DB) and then stores the video file on a MongoDB database. Then it puts a message on a RabbitMQ queue to let the video Converter-service know that there is a pending video file that needs converting.

The Converter-service gets the file ID of the uploaded video in the MongoDB database from the RabbitMQ message, converts the video and stores the converted MP3 on another MongoDB database of completed MP3's. The Converter-service now puts a new message on the RabbitMQ queue that the MP3 file is now ready to be downloaded.

The Notification-service consumes this RabbitMQ message and sends out an email to the user that the MP3 file is ready to download.
The email will contain a unique ID for the user to use along with their JWT to make a request to the Gateway-service to download the MP3. 

The user will then use their JWT and their newly acquired unique file ID to make a request to the Gateway-service, which will then pull the MP3 file from MongoDB and serve it to the user to download.

Each one of these services is a Kubernetes deployment of pods.

# My environment

I originally was going to spin up a VM solely for this but decided to see how viable Windows with WSL would be. Turns out pretty well.

I used:
- Ubuntu as the host OS through WSL, *Windows Subsystem for Linux*. 
- Visual Studio Code connected to Ubuntu using WSL remote connection.
- Docker Desktop using Kubernetes option turned on along with K9s as an extension.
- NGINX installed in K8s to act as the default Ingress for Kubernetes.
- MySQL and MongoDB installed locally on Ubuntu outside of the K8s cluster.



# How to run
Once you have the MySQL database built with your username(email)/password, and all the pods are up and running you can login and obtain your JWT to make subsequent authorized requests. 

## Obtain a JWT
```
curl -X POST http://mp3converter.com/login -u yourusername@email.com:Password@123
```
Example output: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Impkb3Ife4c0MUBnbWFpbC5jb20iLCJleHAiOjE3MDUxOTgSeWgBhTsImlhdCI6MTcwNTExMTk2NiwiYWRtaW4iOnRydWV9.FXhKzKY4aD55H-k2038wfHj$JlPGZpzvCz6Kwr2-rfJ2Ws`

## Upload a video file
Where `video.mp4` is the name of the video file to convert, and is in the same directory we are running this command in.
```
curl -X POST -F 'file=@./video.mp4' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Impkb3Ife4c0MUBnbWFpbC5jb20iLCJleHAiOjE3MDUxOTgSeWgBhTsImlhdCI6MTcwNTExMTk2NiwiYWRtaW4iOnRydWV9.FXhKzKY4aD55H-k2038wfHj$JlPGZpzvCz6Kwr2-rfJ2Ws' http://mp3converter.com/upload
```
If you setup the SMTP server you should receive an email with the unique file ID to use in the download request. Here we will say our file ID received was `65a1f224645ef552da986f6f` which we will append to the download request URL.


## Download the converted MP3 file
```
curl --output mp3_download.mp3 -X GET -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Impkb3Ife4c0MUBnbWFpbC5jb20iLCJleHAiOjE3MDUxOTgSeWgBhTsImlhdCI6MTcwNTExMTk2NiwiYWRtaW4iOnRydWV9.FXhKzKY4aD55H-k2038wfHj$JlPGZpzvCz6Kwr2-rfJ2Ws' "http://mp3converter.com/download?fid=65a1f224645ef552da986f6f"
```
