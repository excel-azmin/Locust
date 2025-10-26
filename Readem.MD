
# Run Application

```
export LOCUST_NO_VERIFY_SSL=true
locust -f locustfile.py --host=https://dev-training.arcapps.org

# Another approach

locust -f locustfile.py --host=https://dev-training.arcapps.org --no-tls-verify
```