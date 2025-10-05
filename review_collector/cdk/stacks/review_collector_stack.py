"""
CDK Stack for Review Collector System with SerpAPI

This stack creates:
- Lambda Functions for SerpAPI-based review collection and news collection
- Lambda Layer for shared code
- Step Functions State Machine for orchestration
- API Gateway for HTTP access
- DynamoDB table for storing reviews
- Secrets Manager for API keys
"""

from pathlib import Path
from typing import Dict, Any
import json

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_logs as logs,
)
from constructs import Construct


class ReviewCollectorStack(Stack):
    """
    CDK Stack for SerpAPI-based Review Collector.
    
    Architecture:
    - Single Lambda function for all review sources (App Store, Google Play, Trustpilot)
    - Lambda Layer for shared domain/application/infrastructure code
    - API Gateway for on-demand collection
    - DynamoDB for review storage
    - Secrets Manager for SerpAPI key
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Base path for Lambda code
        base_path = Path(__file__).parent.parent.parent / "src"
        
        # 1. Create DynamoDB Tables
        reviews_table = self._create_dynamodb_table()
        processed_data_table = self._create_processed_data_table()
        
        # 2. Create Secrets Manager Secret
        secret = self._create_secrets_manager()
        
        # 3. Create Lambda Layer for shared code
        shared_layer = self._create_shared_layer(base_path)
        
        # 4. Create Lambda Function for SerpAPI collection
        serpapi_lambda = self._create_serpapi_lambda(
            base_path=base_path,
            table=reviews_table,
            secret=secret,
            shared_layer=shared_layer
        )
        
        # 5. Create Lambda Function for News collection
        news_lambda = self._create_news_lambda(
            base_path=base_path,
            table=reviews_table,
            secret=secret,
            shared_layer=shared_layer
        )
        
        # 6. Create Lambda Function for Reddit collection
        reddit_lambda = self._create_reddit_lambda(
            base_path=base_path,
            table=reviews_table,
            secret=secret,
            shared_layer=shared_layer
        )
        
        # 7. NEW: Create orchestration Lambda functions
        initializer_lambda = self._create_initializer_lambda(base_path)
        http_caller_lambda = self._create_http_caller_lambda(base_path)
        
        # 8. NEW: Create Step Functions State Machine
        state_machine = self._create_state_machine(
            serpapi_lambda=serpapi_lambda,
            news_lambda=news_lambda,
            reddit_lambda=reddit_lambda,
            initializer_lambda=initializer_lambda,
            http_caller_lambda=http_caller_lambda
        )
        
        # 9. Create API Gateway (with new endpoint)
        api = self._create_api_gateway(
            serpapi_lambda=serpapi_lambda,
            news_lambda=news_lambda,
            reddit_lambda=reddit_lambda,
            state_machine=state_machine,
            reviews_table=reviews_table
        )
    
    def _create_dynamodb_table(self) -> dynamodb.Table:
        """Create DynamoDB table for storing reviews with pk as primary key."""
        table = dynamodb.Table(
            self,
            "ReviewsTableV2",
            table_name="ReviewsTableV2",
            partition_key=dynamodb.Attribute(
                name="pk",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        
        # GSI for querying by brand
        table.add_global_secondary_index(
            index_name="brand-created_at-index",
            partition_key=dynamodb.Attribute(
                name="brand",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        return table
    
    def _create_processed_data_table(self) -> dynamodb.Table:
        """
        Create DynamoDB table for storing processed review data.
        
        Schema:
        - id (pk): Unique identifier for the processed review
        - source: Source platform (e.g., "app_store", "google_play", "trustpilot")
        - backlink: URL to original review
        - text: Review text content
        - rating: Numeric rating (0-5)
        - created_at: ISO timestamp when review was created
        - sentiment: Sentiment analysis result (e.g., "positive", "negative", "neutral")
        - description: Additional description or summary
        - category: Review category classification
        - isProcessed: Boolean flag indicating processing status
        """
        table = dynamodb.Table(
            self,
            "ProcessedDataTable",
            table_name="ProcessedDataTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )
        
        # GSI for querying by source and created_at
        table.add_global_secondary_index(
            index_name="source-created_at-index",
            partition_key=dynamodb.Attribute(
                name="source",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        # GSI for querying by sentiment and created_at
        table.add_global_secondary_index(
            index_name="sentiment-created_at-index",
            partition_key=dynamodb.Attribute(
                name="sentiment",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        # GSI for querying by category and rating
        table.add_global_secondary_index(
            index_name="category-rating-index",
            partition_key=dynamodb.Attribute(
                name="category",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="rating",
                type=dynamodb.AttributeType.NUMBER
            ),
        )
        
        # GSI for querying unprocessed items
        table.add_global_secondary_index(
            index_name="isProcessed-created_at-index",
            partition_key=dynamodb.Attribute(
                name="isProcessed",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
        )
        
        return table
    
    def _create_secrets_manager(self) -> secretsmanager.Secret:
        """Create or reference Secrets Manager secret."""
        # Reference existing secret (created manually with SerpAPI key)
        secret = secretsmanager.Secret.from_secret_name_v2(
            self,
            "ReviewCollectorSecret",
            secret_name="review-collector/credentials"
        )
        
        return secret
    
    def _create_shared_layer(self, base_path: Path) -> lambda_.LayerVersion:
        """Create Lambda Layer for shared code (domain, application, infrastructure)."""
        shared_path = str(base_path / "shared")
        
        layer = lambda_.LayerVersion(
            self,
            "SharedCodeLayer",
            layer_version_name="review-collector-shared",
            code=lambda_.Code.from_asset(
                shared_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "mkdir -p /asset-output/python && "
                        "cp -r . /asset-output/python/"
                    ],
                }
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Shared domain, application, and infrastructure code"
        )
        
        return layer
    
    def _create_serpapi_lambda(
        self,
        base_path: Path,
        table: dynamodb.Table,
        secret: secretsmanager.Secret,
        shared_layer: lambda_.LayerVersion
    ) -> lambda_.Function:
        """Create unified Lambda function for SerpAPI-based collection."""
        src_path = str(base_path / "serpapi_collector")
        
        fn = lambda_.Function(
            self,
            "SerpAPICollectorLambda",
            function_name="serpapi-collector-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            layers=[shared_layer],
            timeout=Duration.seconds(900),  # 15 minutes (max for Lambda)
            memory_size=512,
            environment={
                "TABLE_NAME": table.table_name,
                "SECRET_NAME": secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "review-collector",
                "LOG_LEVEL": "INFO",
            },
        )
        
        # Grant permissions
        table.grant_read_write_data(fn)
        secret.grant_read(fn)
        
        return fn
    
    def _create_news_lambda(
        self,
        base_path: Path,
        table: dynamodb.Table,
        secret: secretsmanager.Secret,
        shared_layer: lambda_.LayerVersion
    ) -> lambda_.Function:
        """Create Lambda function for NewsAPI-based collection."""
        src_path = str(base_path / "news_collector")
        
        fn = lambda_.Function(
            self,
            "NewsCollectorLambda",
            function_name="news-collector-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            layers=[shared_layer],
            timeout=Duration.seconds(900),  # 15 minutes (max for Lambda)
            memory_size=512,
            environment={
                "TABLE_NAME": table.table_name,
                "SECRET_NAME": secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "news-collector",
                "LOG_LEVEL": "INFO",
            },
        )
        
        # Grant permissions
        table.grant_read_write_data(fn)
        secret.grant_read(fn)
        
        return fn
    
    def _create_reddit_lambda(
        self,
        base_path: Path,
        table: dynamodb.Table,
        secret: secretsmanager.Secret,
        shared_layer: lambda_.LayerVersion
    ) -> lambda_.Function:
        """Create Lambda function for Reddit-based collection."""
        src_path = str(base_path / "reddit_collector")
        
        fn = lambda_.Function(
            self,
            "RedditCollectorLambda",
            function_name="reddit-collector-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            layers=[shared_layer],
            timeout=Duration.seconds(900),  # 15 minutes (max for Lambda)
            memory_size=512,
            environment={
                "TABLE_NAME": table.table_name,
                "SECRET_NAME": secret.secret_name,
                "POWERTOOLS_SERVICE_NAME": "reddit-collector",
                "LOG_LEVEL": "INFO",
            },
        )
        
        # Grant permissions
        table.grant_read_write_data(fn)
        secret.grant_read(fn)
        
        return fn
    
    def _create_initializer_lambda(self, base_path: Path) -> lambda_.Function:
        """Create Lambda function for initializing report generation"""
        src_path = str(base_path / "report_initializer")
        
        fn = lambda_.Function(
            self,
            "ReportInitializerLambda",
            function_name="report-initializer-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(src_path),
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
            }
        )
        
        return fn
    
    def _create_http_caller_lambda(self, base_path: Path) -> lambda_.Function:
        """Create Lambda function for calling external HTTP endpoint"""
        src_path = str(base_path / "http_caller")
        
        fn = lambda_.Function(
            self,
            "HttpCallerLambda",
            function_name="http-caller-lambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(
                src_path,
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && "
                        "cp -r . /asset-output/"
                    ],
                }
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO",
            }
        )
        
        return fn
    
    def _create_state_machine(
        self,
        serpapi_lambda: lambda_.Function,
        news_lambda: lambda_.Function,
        reddit_lambda: lambda_.Function,
        initializer_lambda: lambda_.Function,
        http_caller_lambda: lambda_.Function
    ) -> sfn.StateMachine:
        """Create Step Functions State Machine for orchestrating report generation"""
        
        # Task 1: Initialize job (generate job_id, prepare params)
        initialize_task = tasks.LambdaInvoke(
            self, "InitializeJob",
            lambda_function=initializer_lambda,
            output_path="$.Payload",
            comment="Generate job_id and prepare parameters"
        )
        
        # Task 2: Collect from App Store (with error handling)
        appstore_task = tasks.LambdaInvoke(
            self, "CollectAppStore",
            lambda_function=serpapi_lambda,
            payload=sfn.TaskInput.from_object({
                "source": "appstore",
                "app_identifier": sfn.JsonPath.string_at("$.sources.appstore"),
                "brand": sfn.JsonPath.string_at("$.brand"),
                "limit": sfn.JsonPath.number_at("$.limit"),
                "job_id": sfn.JsonPath.string_at("$.job_id")
            }),
            result_selector={
                "source": "appstore",
                "success": True,
                "data.$": "$.Payload"
            },
            comment="Collect reviews from App Store"
        ).add_catch(
            sfn.Pass(
                self, "AppStoreError",
                result=sfn.Result.from_object({
                    "source": "appstore",
                    "success": False,
                    "error": "Collection failed or data source not available"
                })
            ),
            errors=["States.ALL"]
        )
        
        # Task 3: Collect from Google Play (with error handling)
        googleplay_task = tasks.LambdaInvoke(
            self, "CollectGooglePlay",
            lambda_function=serpapi_lambda,
            payload=sfn.TaskInput.from_object({
                "source": "googleplay",
                "app_identifier": sfn.JsonPath.string_at("$.sources.googleplay"),
                "brand": sfn.JsonPath.string_at("$.brand"),
                "limit": sfn.JsonPath.number_at("$.limit"),
                "job_id": sfn.JsonPath.string_at("$.job_id")
            }),
            result_selector={
                "source": "googleplay",
                "success": True,
                "data.$": "$.Payload"
            },
            comment="Collect reviews from Google Play"
        ).add_catch(
            sfn.Pass(
                self, "GooglePlayError",
                result=sfn.Result.from_object({
                    "source": "googleplay",
                    "success": False,
                    "error": "Collection failed or data source not available"
                })
            ),
            errors=["States.ALL"]
        )
        
        # Task 4: Collect from Trustpilot (with error handling)
        trustpilot_task = tasks.LambdaInvoke(
            self, "CollectTrustpilot",
            lambda_function=serpapi_lambda,
            payload=sfn.TaskInput.from_object({
                "source": "trustpilot",
                "app_identifier": sfn.JsonPath.string_at("$.sources.trustpilot"),
                "brand": sfn.JsonPath.string_at("$.brand"),
                "limit": sfn.JsonPath.number_at("$.limit"),
                "job_id": sfn.JsonPath.string_at("$.job_id")
            }),
            result_selector={
                "source": "trustpilot",
                "success": True,
                "data.$": "$.Payload"
            },
            comment="Collect reviews from Trustpilot"
        ).add_catch(
            sfn.Pass(
                self, "TrustpilotError",
                result=sfn.Result.from_object({
                    "source": "trustpilot",
                    "success": False,
                    "error": "Collection failed or data source not available"
                })
            ),
            errors=["States.ALL"]
        )
        
        # Task 5: Collect News (with error handling)
        news_task = tasks.LambdaInvoke(
            self, "CollectNews",
            lambda_function=news_lambda,
            payload=sfn.TaskInput.from_object({
                "brand": sfn.JsonPath.string_at("$.brand"),
                "limit": sfn.JsonPath.number_at("$.limit"),
                "job_id": sfn.JsonPath.string_at("$.job_id")
            }),
            result_selector={
                "source": "news",
                "success": True,
                "data.$": "$.Payload"
            },
            comment="Collect news articles"
        ).add_catch(
            sfn.Pass(
                self, "NewsError",
                result=sfn.Result.from_object({
                    "source": "news",
                    "success": False,
                    "error": "Collection failed or data source not available"
                })
            ),
            errors=["States.ALL"]
        )
        
        # Task 6: Collect from Reddit (with error handling)
        reddit_task = tasks.LambdaInvoke(
            self, "CollectReddit",
            lambda_function=reddit_lambda,
            payload=sfn.TaskInput.from_object({
                "brand": sfn.JsonPath.string_at("$.brand"),
                "keywords": sfn.JsonPath.string_at("$.reddit_keywords"),
                "limit": sfn.JsonPath.number_at("$.limit"),
                "days_back": 30,
                "job_id": sfn.JsonPath.string_at("$.job_id")
            }),
            result_selector={
                "source": "reddit",
                "success": True,
                "data.$": "$.Payload"
            },
            comment="Collect Reddit posts"
        ).add_catch(
            sfn.Pass(
                self, "RedditError",
                result=sfn.Result.from_object({
                    "source": "reddit",
                    "success": False,
                    "error": "Collection failed or data source not available"
                })
            ),
            errors=["States.ALL"]
        )
        
        # Parallel state - run all collections simultaneously
        parallel_collection = sfn.Parallel(
            self, "ParallelCollection",
            result_path="$.collection_results",
            comment="Collect data from all sources in parallel"
        )
        parallel_collection.branch(appstore_task)
        parallel_collection.branch(googleplay_task)
        parallel_collection.branch(trustpilot_task)
        parallel_collection.branch(news_task)
        parallel_collection.branch(reddit_task)
        
        # Task 6: Call external processing endpoint
        call_processing_endpoint = tasks.LambdaInvoke(
            self, "CallProcessingEndpoint",
            lambda_function=http_caller_lambda,
            payload=sfn.TaskInput.from_object({
                "endpoint_url": "https://webhook.site/test-endpoint",  # Hardcoded stub
                "job_id": sfn.JsonPath.string_at("$.job_id"),
                "brand": sfn.JsonPath.string_at("$.brand"),
                "collection_results": sfn.JsonPath.string_at("$.collection_results")
            }),
            result_selector={
                "success": True,
                "response.$": "$.Payload"
            },
            result_path="$.processing_result",
            comment="Call external processing endpoint with collected data"
        ).add_catch(
            sfn.Pass(
                self, "ProcessingCallError",
                result=sfn.Result.from_object({
                    "success": False,
                    "error": "Failed to call processing endpoint"
                })
            ),
            errors=["States.ALL"],
            result_path="$.processing_result"
        )
        
        # Final success state
        success_state = sfn.Succeed(
            self, "ReportGenerationComplete",
            comment="Report generation completed successfully"
        )
        
        # Chain: Initialize → Parallel Collection → Call External API → Success
        definition = initialize_task \
            .next(parallel_collection) \
            .next(call_processing_endpoint) \
            .next(success_state)
        
        # Create CloudWatch Logs group for state machine
        log_group = logs.LogGroup(
            self,
            "StateMachineLogGroup",
            log_group_name="/aws/stepfunctions/review-collector",
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Create the state machine
        state_machine = sfn.StateMachine(
            self,
            "ReviewCollectorStateMachine",
            state_machine_name="ReviewCollectorStateMachine",
            definition=definition,
            timeout=Duration.minutes(15),
            tracing_enabled=True,
            logs=sfn.LogOptions(
                destination=log_group,
                level=sfn.LogLevel.ALL
            ),
            comment="Orchestrates review and news collection from multiple sources"
        )
        
        # ⚠️ ВАЖЛИВО: Grant permissions for Step Functions to invoke Lambda functions
        serpapi_lambda.grant_invoke(state_machine)
        news_lambda.grant_invoke(state_machine)
        reddit_lambda.grant_invoke(state_machine)
        initializer_lambda.grant_invoke(state_machine)
        http_caller_lambda.grant_invoke(state_machine)
        
        return state_machine
    
    def _create_api_gateway(
        self,
        serpapi_lambda: lambda_.Function,
        news_lambda: lambda_.Function,
        reddit_lambda: lambda_.Function,
        state_machine: sfn.StateMachine,
        reviews_table: dynamodb.Table
    ) -> apigateway.RestApi:
        """Create API Gateway for HTTP access."""
        api = apigateway.RestApi(
            self,
            "ReviewCollectorAPI",
            rest_api_name="Review Collector API",
            description="API for on-demand review and news collection with orchestration",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )
        
        # Integration for review collection
        review_integration = apigateway.LambdaIntegration(
            serpapi_lambda,
            proxy=True,
            allow_test_invoke=True,
        )
        
        # POST /collect-reviews endpoint
        collect_reviews_resource = api.root.add_resource("collect-reviews")
        collect_reviews_resource.add_method("POST", review_integration)
        
        # Add CORS for reviews
        collect_reviews_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # Integration for news collection
        news_integration = apigateway.LambdaIntegration(
            news_lambda,
            proxy=True,
            allow_test_invoke=True,
        )
        
        # POST /collect-news endpoint
        collect_news_resource = api.root.add_resource("collect-news")
        collect_news_resource.add_method("POST", news_integration)
        
        # Add CORS for news
        collect_news_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # Integration for Reddit collection
        reddit_integration = apigateway.LambdaIntegration(
            reddit_lambda,
            proxy=True,
            allow_test_invoke=True,
        )
        
        # POST /collect-reddit endpoint
        collect_reddit_resource = api.root.add_resource("collect-reddit")
        collect_reddit_resource.add_method("POST", reddit_integration)
        
        # Add CORS for reddit
        collect_reddit_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # NEW: Integration for Step Functions (generate report)
        # ⚠️ ВАЖЛИВО: Create IAM role for API Gateway to start Step Functions execution
        api_sfn_role = iam.Role(
            self,
            "ApiGatewayStepFunctionsRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            description="Role for API Gateway to start Step Functions execution"
        )
        
        # Grant API Gateway permission to start Step Functions execution
        state_machine.grant_start_execution(api_sfn_role)
        state_machine.grant_read(api_sfn_role)
        
        # Create Step Functions integration (async execution)
        sfn_integration = apigateway.AwsIntegration(
            service="states",
            action="StartExecution",
            integration_http_method="POST",
            options=apigateway.IntegrationOptions(
                credentials_role=api_sfn_role,
                request_templates={
                    "application/json": json.dumps({
                        "stateMachineArn": state_machine.state_machine_arn,
                        "input": "$util.escapeJavaScript($input.json('$'))"
                    })
                },
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"message": "Report generation started", "executionArn": "$input.json(\'$.executionArn\')", "startDate": "$input.json(\'$.startDate\')"}'
                        }
                    ),
                    apigateway.IntegrationResponse(
                        status_code="500",
                        selection_pattern=".*error.*",
                        response_templates={
                            "application/json": '{"error": "Failed to start Step Functions execution"}'
                        }
                    )
                ]
            )
        )
        
        # POST /generate-report endpoint
        generate_report_resource = api.root.add_resource("generate-report")
        generate_report_resource.add_method(
            "POST",
            sfn_integration,
            method_responses=[
                apigateway.MethodResponse(status_code="200"),
                apigateway.MethodResponse(status_code="500")
            ]
        )
        
        # Add CORS for generate-report
        generate_report_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        
        # Stack outputs
        from aws_cdk import CfnOutput
        
        CfnOutput(
            self,
            "ApiUrl",
            value=api.url,
            description="API Gateway URL"
        )
        
        CfnOutput(
            self,
            "CollectReviewsEndpoint",
            value=f"{api.url}collect-reviews",
            description="Collect Reviews Endpoint"
        )
        
        CfnOutput(
            self,
            "CollectNewsEndpoint",
            value=f"{api.url}collect-news",
            description="Collect News Endpoint"
        )
        
        CfnOutput(
            self,
            "GenerateReportEndpoint",
            value=f"{api.url}generate-report",
            description="Generate Report Endpoint (Step Functions Orchestration)"
        )
        
        CfnOutput(
            self,
            "ReviewLambdaFunctionName",
            value=serpapi_lambda.function_name,
            description="Review Lambda Function Name"
        )
        
        CfnOutput(
            self,
            "NewsLambdaFunctionName",
            value=news_lambda.function_name,
            description="News Lambda Function Name"
        )
        
        CfnOutput(
            self,
            "StateMachineArn",
            value=state_machine.state_machine_arn,
            description="Step Functions State Machine ARN"
        )
        
        CfnOutput(
            self,
            "DynamoDBTableName",
            value=reviews_table.table_name,
            description="DynamoDB Table Name"
        )
        
        return api
