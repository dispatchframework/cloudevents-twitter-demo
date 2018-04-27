## Dispatch CloudEvents Demo

This repo contains the code for running Dispatch with the CloudEvents Demo.

The demo producers will send blob store/image related CloudEvents into Dispatch,
which will then watermark, scale, and send the image to a twitter feed.


More information can be found in these repos:

- https://github.com/ac360/cloudevents-demo
- https://github.com/clemensv/azure-cloudevents-bridge

### To deploy the demo:
1. Create an application in your twitter feed, add the credentials
to a secrets file (do NOT check in this file), and add to Dispatch.
A sample (empty) file is provided.
   ```
   cp secrets_sample.json secrets.json
   vi secrets.json
   dispatch create secret twitter-secrets secrets.json
   ```

1. Create a new image containing our dependencies
   ```
   dispatch create image python3-twitter python3-base --runtime-deps requirements.txt
   ```

1. Create the function using the image and attach the secrets to it
   ```
   dispatch create function python3-twitter twitter twitter.py --secret twitter-secrets
   ```

1. Create the API gateway binding.
   ```
   dispatch create api --method POST --path /twitter post-twitter twitter
   ```

1. Sample Postman test cases can be found in the repo.
