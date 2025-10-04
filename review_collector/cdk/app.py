#!/usr/bin/env python3
"""
CDK App Entry Point

Defines the main CDK application and stacks.
"""

import os
from aws_cdk import App, Environment
from stacks.review_collector_stack import ReviewCollectorStack


# Define AWS environment
env = Environment(
    account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
    region=os.environ.get('CDK_DEFAULT_REGION', 'us-east-1')
)

# Create CDK app
app = App()

# Deploy Review Collector stack
ReviewCollectorStack(
    app,
    "ReviewCollectorStack",
    env=env,
    description="Serverless review collector from App Store, Google Play, and Trustpilot"
)

# Synthesize CloudFormation template
app.synth()

