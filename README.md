# Locust API Load Testing

A performance testing suite for the Training API using Locust, designed to test and monitor API endpoints under various load conditions.

## Overview

This project contains Locust test scripts to perform load testing on the Training Management API. It includes features for concurrent user simulation, response logging, and comprehensive performance metrics collection.

## Features

- Load testing for Training API endpoints
- Automated response data collection to CSV
- SSL/TLS handling for secure endpoints
- Configurable user wait times and request patterns
- Real-time performance metrics tracking
- Detailed request/response logging

## Project Structure

```
Locust/
├── locustfile.py                  # Full-featured test with CSV logging
├── locustfile_training_list.py    # Training list endpoint testing
├── locust_registration.py         # Registration endpoint testing
├── registration.csv                # Sample registration data
├── training_api_responses.csv     # Generated response data (created on run)
├── venv/                          # Python virtual environment
└── README.md                      # This file
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Network access to the target API

## Installation

### 1. Clone or navigate to the project directory

```bash
cd /home/azmin/Desktop/arcapps/Locust
```

### 2. Create a virtual environment (if not already created)

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 4. Install required packages

```bash
pip install locust
```

## Configuration

### Environment Variables

For SSL certificate verification bypass:

```bash
export LOCUST_NO_VERIFY_SSL=true
```

### Test Files

#### locustfile.py (Advanced)
- Full-featured test with CSV logging
- Tracks request counter, timestamps, and response metrics
- Saves training titles and pagination data
- Records response times in milliseconds

#### locustfile_training_list.py
- Training list endpoint testing
- GET endpoint testing for retrieving training sessions

#### locust_registration.py
- Registration endpoint testing
- POST endpoint testing with CSV data
- Tests user registration workflow with sample data from registration.csv

## Usage

### Running Tests

#### Option 1: Web UI Mode (Recommended)

Start Locust with the web interface:

```bash
locust -f locustfile.py --host=https://dev-training.arcapps.org
```

Then open your browser and navigate to:
```
http://localhost:8089
```

Configure:
- Number of users to simulate
- Spawn rate (users per second)
- Test duration (optional)

#### Option 2: Web UI with SSL Verification Disabled

```bash
locust -f locustfile.py --host=https://dev-training.arcapps.org --no-tls-verify
```

#### Option 3: Headless Mode (CLI)

Run tests without the web UI:

```bash
locust -f locustfile.py --host=https://dev-training.arcapps.org \
  --headless \
  --users 10 \
  --spawn-rate 2 \
  --run-time 60s
```

Parameters:
- `--users 10`: Simulate 10 concurrent users
- `--spawn-rate 2`: Add 2 users per second
- `--run-time 60s`: Run for 60 seconds

#### Option 4: Testing Registration Endpoint

```bash
locust -f locust_registration.py --host=https://dev-training.arcapps.org
```

This will test the registration endpoint using sample data from [registration.csv](registration.csv).

### Example Commands

```bash
# Basic test with 5 users
locust -f locustfile.py --host=https://dev-training.arcapps.org --headless -u 5 -r 1 -t 30s

# Stress test with 100 users
locust -f locustfile.py --host=https://dev-training.arcapps.org --headless -u 100 -r 10 -t 5m

# Extended load test
locust -f locustfile.py --host=https://dev-training.arcapps.org --headless -u 50 -r 5 -t 30m
```

## API Endpoints Being Tested

### GET /api/v1/training/list-for-user

**Description:** Retrieves a paginated list of training sessions

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 6)
- `fromDate`: Filter start date (format: YYYY-MM-DD)
- `toDate`: Filter end date (format: YYYY-MM-DD)
- `dateField`: Date field to filter on (e.g., 'startDateTime')
- `select`: Comma-separated fields to return

**Expected Response:**
```json
{
  "response": {
    "training": [
      {
        "_id": "string",
        "title": "string",
        "startDateTime": "ISO date",
        "endDateTime": "ISO date",
        "trainerName": "string",
        "trainerDesignation": "string",
        "trainingVenue": "string",
        "lastRegistrationDateTime": "ISO date"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 6,
      "hasNext": false
    }
  }
}
```

### POST /api/v1/training/register

**Description:** Registers a user for a training session

**Test Script:** [locust_registration.py](locust_registration.py)

**Request Body:**
```json
{
  "training": "training_id",
  "phone": "01XXXXXXXXX",
  "nid": "XXXXXXXXXXX",
  "designation": "User designation",
  "office": "User office/organization"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Registration successful"
}
```

**Test Data Source:** [registration.csv](registration.csv)

## Output Data

### CSV Export (locustfile.py)

The test automatically generates `training_api_responses.csv` with the following columns:

| Column | Description |
|--------|-------------|
| counter | Sequential request number |
| timestamp | ISO format timestamp of request |
| status_code | HTTP status code |
| response_time_ms | Response time in milliseconds |
| total_trainings | Number of trainings returned |
| page | Page number from response |
| limit | Limit value from response |
| has_next_page | Whether more pages are available |
| training_titles | Pipe-separated list of training titles |

### Locust Reports

After running tests, Locust generates:
- Real-time statistics in the web UI
- Request success/failure rates
- Response time percentiles (50th, 66th, 75th, 80th, 90th, 95th, 98th, 99th, 100th)
- Requests per second (RPS)
- Number of failures and exceptions

You can download reports as:
- HTML report
- CSV statistics
- CSV exceptions

## Understanding Test Results

### Key Metrics to Monitor

1. **Response Time**: Should remain consistent under load
2. **Failure Rate**: Should be 0% or near 0%
3. **Requests/sec**: Indicates throughput capacity
4. **95th Percentile**: Shows response time for 95% of requests

### Success Criteria

- HTTP 200 status codes
- Response times < 1000ms for 95th percentile
- 0% error rate
- Consistent throughput

### Failure Scenarios

The test handles:
- HTTP errors (non-200 status codes)
- Connection failures (status code 0)
- SSL/TLS issues
- JSON decode errors
- Network timeouts

## Customization

### Adjusting Test Parameters

Edit [locustfile.py](locustfile.py) to modify:

**Wait Time** (line 8):
```python
wait_time = between(1, 3)  # Wait 1-3 seconds between requests
```

**API Parameters** (lines 75-82):
```python
params = {
    'page': 1,
    'limit': 6,
    'fromDate': '2025-10-26',
    'toDate': '2026-02-26',
    'dateField': 'startDateTime',
    'select': '_id,title,...'
}
```

**Task Weight** (line 72):
```python
@task(1)  # Higher number = higher frequency
```

### Adding New Test Tasks

```python
@task(2)  # Will run twice as often as task(1)
def test_another_endpoint(self):
    """Test a different endpoint"""
    with self.client.get(
        "/api/v1/another/endpoint",
        name="AnotherEndpoint",
        catch_response=True
    ) as response:
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"HTTP {response.status_code}")
```

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL verification errors:

```bash
# Use --no-tls-verify flag
locust -f locustfile.py --host=https://dev-training.arcapps.org --no-tls-verify

# Or set environment variable
export LOCUST_NO_VERIFY_SSL=true
locust -f locustfile.py --host=https://dev-training.arcapps.org
```

### Connection Refused

- Verify the API host is accessible
- Check if VPN is required
- Ensure the API server is running

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall locust
pip install --upgrade locust
```

### CSV File Locked

- Close any programs (Excel, etc.) that have the CSV file open
- The file is created/appended during test runs

## Best Practices

1. **Start Small**: Begin with 1-5 users to verify the test works
2. **Gradual Ramp-up**: Increase load gradually to find breaking points
3. **Monitor Server**: Watch server resources during tests
4. **Clean Data**: Delete CSV file between test runs for fresh data
5. **Document Results**: Save HTML reports for comparison
6. **Test Off-Peak**: Run heavy load tests during off-peak hours

## Environment-Specific Testing

### Development
```bash
locust -f locustfile.py --host=https://dev-training.arcapps.org
```

### Staging
```bash
locust -f locustfile.py --host=https://staging-training.arcapps.org
```

### Production (Use with Caution)
```bash
locust -f locustfile.py --host=https://training.arcapps.org -u 5 -r 1
```

## Contributing

When adding new tests:
1. Follow existing code structure
2. Add appropriate error handling
3. Include descriptive task names
4. Update this README with new endpoints

## Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [Writing Locust Tests](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Locust Configuration](https://docs.locust.io/en/stable/configuration.html)

## Support

For issues or questions:
- Check the Locust documentation
- Review test logs and CSV output
- Verify API endpoint availability
- Check network connectivity and SSL configuration

## License

Internal project for API testing purposes.
