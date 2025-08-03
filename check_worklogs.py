#!/usr/bin/env python3
import requests

# Test worklogs for parvesh.thapa
print("Testing worklogs for parvesh.thapa...")

# First connect
connect_response = requests.post(
    'http://localhost:8000/api/connect',
    params={
        'server': 'https://wideorbit.atlassian.net',
        'email': 'parvesh.thapa@wideorbit.com',
        'api_token': 'ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA'
    }
)

print(f"Connect status: {connect_response.status_code}")

# Then get worklogs
worklogs_response = requests.get(
    'http://localhost:8000/api/user/parvesh.thapa/worklogs',
    params={'days': 7}
)

print(f"Worklogs status: {worklogs_response.status_code}")
print(f"Worklogs response: {worklogs_response.text}") 